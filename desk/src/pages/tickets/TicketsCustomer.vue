<template>
  <div class="flex flex-col">
    <PageTitle title="Tickets">
      <template #right>
        <div class="flex gap-2">
          <div
            class="flex items-center justify-between text-base text-gray-700"
          >
            <div class="flex gap-3">
              <Dropdown :options="dropdownOptions">
                <template #default="{ open }">
                  <Button
                    :label="dropdownTitle"
                    :icon-right="open ? 'chevron-up' : 'chevron-down'"
                    theme="gray"
                    variant="outline"
                  />
                </template>
              </Dropdown>
            <!-- </div> -->
            <!-- <div class="flex gap-4"> -->
              <Dropdown :options="projectFilters">
                <template #default="{ open }">
                  <Button
                    :label="projectTitle"
                    :icon-right="open ? 'chevron-up' : 'chevron-down'"
                    theme="gray"
                    variant="outline"
                  />
                </template>
              </Dropdown>
            </div>

            <!-- <ViewControls
      :filter="{ filters: filters, filterableFields: filterableFields.data }"
      :sort="{ sorts: sorts, sortableFields: sortableFields.data }"
      :column="{
        fields: fields,
        columns: columns,
      }"
      @event:sort="processSorts"
      @event:filter="processFilters"
      @event:column="processColumns"
    /> -->

          </div>
          <RouterLink
            v-if="!configStore.preferKnowledgeBase"
            :to="{ name: CUSTOMER_PORTAL_NEW_TICKET }"
          >
            <Button
              class="bg-gray-900 text-white hover:bg-gray-800"
              label="New ticket"
              icon-right="plus"
            />
          </RouterLink>
        </div>
      </template>
    </PageTitle>
    <ListView
      :columns="columns1"
      :resource="tickets"
      class="mt-2.5"
      doctype="HD Ticket"
    >
      <template #status="{ data }">
        <Badge
          :label="transformStatus(data.status)"
          :theme="ticketStatusStore.colorMap[data.status]"
          variant="outline"
        />
      </template>
      <template #response_by="{ data }">
        <span v-if="data.response_by">
          <Badge
            v-if="
              data.first_responded_on &&
              dayjs(data.first_responded_on).isBefore(data.response_by)
            "
            label="Fulfilled"
            theme="green"
            variant="outline"
          />
          <Badge
            v-else-if="dayjs(data.first_responded_on).isAfter(data.response_by)"
            label="Failed"
            theme="red"
            variant="outline"
          />
          <Tooltip v-else :text="dayjs(data.response_by).long()">
            {{ dayjs(data.response_by).fromNow() }}
          </Tooltip>
        </span>
      </template>
      <template #resolution_by="{ data }">
        <span v-if="data.resolution_by">
          <Badge
            v-if="
              data.resolution_date &&
              dayjs(data.resolution_date).isBefore(data.resolution_by)
            "
            label="Fulfilled"
            theme="green"
            variant="outline"
          />
          <Badge
            v-else-if="dayjs(data.resolution_date).isAfter(data.resolution_by)"
            label="Failed"
            theme="red"
            variant="outline"
          />
          <Tooltip v-else :text="dayjs(data.resolution_by).long()">
            {{ dayjs(data.resolution_by).fromNow() }}
          </Tooltip>
        </span>
      </template>
      <template #creation="{ data }">
        {{ dayjs(data.creation).fromNow() }}
      </template>
    </ListView>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Dropdown, Tooltip } from "frappe-ui";
import { dayjs } from "@/dayjs";
import { useConfigStore } from "@/stores/config";
import { useTicketStatusStore } from "@/stores/ticketStatus";
import { createListManager } from "@/composables/listManager";
import { CUSTOMER_PORTAL_TICKET, CUSTOMER_PORTAL_NEW_TICKET } from "@/router";
import { ListView } from "@/components";
import PageTitle from "@/components/PageTitle.vue";
import { ViewControls, LayoutHeader } from "@/components";
import { createResource, Breadcrumbs, createListResource } from "frappe-ui";
import { useStorage } from "@vueuse/core";
import { late } from "zod";

let storage = useStorage("tickets_agent", {
  filtersToApply: {},
  filters: [],
  sorts: [],
  sortsToApply: "modified desc",
  columns: [],
  rows: [],
  pageLength: 20,
});


let columns = storage.value.columns ? storage.value.columns : [];
let rows = storage.value.rows ? storage.value.rows : [];

let filtersToApply = storage.value.filtersToApply;
let filters = ref(storage.value.filters);

let sorts = ref(storage.value.sorts);
let sortsToApply = storage.value.sortsToApply;

let pageLength = ref(storage.value.pageLength);
let pageLengthCount = pageLength.value;

const configStore = useConfigStore();
const ticketStatusStore = useTicketStatusStore();
const columns1 = [
  {
    label: "#",
    key: "name",
    width: "w-12",
  },
  {
    label: "Subject",
    key: "subject",
    width: "w-96",
  },
  {
    label: "Status",
    key: "status",
    width: "w-32",
  },
  {
    label: "Project",
    key: "project",
    width: "w-32",
  },
  {
    label: "Priority",
    key: "priority",
    width: "w-32",
  },
  {
    label: "First Response",
    key: "response_by",
    width: "w-32",
  },
  {
    label: "Resolution",
    key: "resolution_by",
    width: "w-32",
  },
  {
    label: "Created",
    key: "creation",
    width: "w-32",
  },
];

const temp_projectFilters = ref([]); // Define project_list
const projectTitle = ref("Select Project");
const projectFilters = ref([]);


createListResource({
  doctype: 'Project',
  url: "helpdesk.helpdesk.doctype.hd_ticket.api.get_projects_for_filter",
  auto: true,
  onError(error) {
    console.log("Error", error);
  },
  onSuccess(data) {
    temp_projectFilters.value = data; // Update projectList with the fetched data
   
      temp_projectFilters.value.forEach(item => {
          projectFilters.value.push({
            label: item.label,
            onClick() {
              if (item.label === '' || item.label === "Select Project") {
                projectFilter("Select Project", { project: undefined });
              } else {
                projectFilter(item.label, { project: ["in", item.label] });
              }
            }
          });
      });
  },
});



const tickets = createListManager({
  doctype: "HD Ticket",
  pageLength: 20,
  fields: [
    "name",
    "creation",
    "subject",
    "status",
    "priority",
    "response_by",
    "resolution_by",
    "first_responded_on",
    "resolution_date",
    "project"
  ],
  auto: true,
  transform: (data) => {
    for (const d of data) {
      d.onClick = {
        name: CUSTOMER_PORTAL_TICKET,
        params: {
          ticketId: d.name,
        },
      };
    }
  },
});

const ACTIVE_TICKET_TYPES = ["Open", "Replied"];
const dropdownTitle = ref("All tickets");
const dropdownOptions = [
  {
    label: "All tickets",
    onClick() {
      filter("All tickets", { status: undefined });
    },
  },
  {
    label: "Open tickets",
    onClick() {
      filter("Open tickets", { status: ["in", ACTIVE_TICKET_TYPES] });
    },
  },
  {
    label: "Closed tickets",
    onClick() {
      filter("Closed tickets", { status: ["not in", ACTIVE_TICKET_TYPES] });
    },
  },
];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function filter(title: string, filters: Record<string, any>) {
  tickets.update({
    ...tickets,
    filters: {
      ...tickets.filters,
      ...filters,
    },
  });
  tickets.reload();
  dropdownTitle.value = title;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function projectFilter(title: string, filters: Record<string, any>) {
  tickets.update({
    ...tickets,
    filters: {
      ...tickets.filters,
      ...filters,
    },
  });
  tickets.reload();
  projectTitle.value = title;
}

function transformStatus(status: string) {
  switch (status) {
    case "Replied":
      return "Awaiting reply";
    default:
      return status;
  }
}

function processColumns(columnEvent) {
  if (columnEvent.event === "add") {
    columns = [columnEvent.data, ...columns];
    rows = [columnEvent.data.key, ...rows];
  } else if (columnEvent.event === "remove") {
    rows = rows.filter((row) => {
      return row != columnEvent.data.key;
    });
    columns = columns.filter((column) => {
      return column.key != columnEvent.data.key;
    });
  } else if (columnEvent.event === "reset") {
    columns = [];
    rows = [];
  }
  storage.value.columns = columns;
  storage.value.rows = rows;

  apply();
}

function processSorts(sortEvent) {
  if (sortEvent.event === "add") {
    sorts.value.push(sortEvent.data);
    sortsToApply = sortEvent.data.sortToApply;
  } else if (sortEvent.event === "remove") {
    sorts.value.splice(sortEvent.index, 1);
    sortsToApply = sortEvent.data.sortToApply;
  } else if (sortEvent.event === "clear") {
    sorts.value = [];
    sortsToApply = "modified desc";
  } else if (sortEvent.event === "update") {
    sorts.value[sortEvent.data.index] = sortEvent.data;
    sortsToApply = sortEvent.data.sortToApply;
  }

  storage.value.sorts = sorts.value;
  storage.value.sortsToApply = sortsToApply;

  apply();
}

function processFilters(filterEvent) {
  if (filterEvent.event === "add") {
    const key = filterEvent.data.field.fieldname;
    const { filterToApply } = filterEvent.data;

    filters.value.push(filterEvent.data);
    filtersToApply[key] = filterToApply[key];
  } else if (filterEvent.event === "remove") {
    const key = filters.value[filterEvent.index].field.fieldname;
    filters.value.splice(filterEvent.index, 1);
    delete filtersToApply[key];
  } else if (filterEvent.event === "update") {
    const key = filterEvent.data.field.fieldname;
    const oldKey = filters.value[filterEvent.data.index].field.fieldname;

    const { filterToApply } = filterEvent.data;

    filters.value[filterEvent.data.index] = filterEvent.data;
    delete filtersToApply[oldKey];

    filtersToApply[key] = filterToApply[key];
  } else if (filterEvent.event === "clear") {
    filters.value = [];
    for (let filter in filtersToApply) delete filtersToApply[filter];
  } else if (filterEvent.event === "preset") {
    filters.value = filterEvent.data.filters;

    for (let filter in filtersToApply) delete filtersToApply[filter];
    Object.assign(filtersToApply, filterEvent.data.filtersToApply);
  }

  storage.value.filters = filters.value;
  storage.value.filtersToApply = filtersToApply;

  apply();
}

function apply() {
  tickets.update({
    params: {
      order_by: sortsToApply,
      filters: filtersToApply,
      page_length: pageLengthCount,
      doctype: "HD Ticket",
      columns: columns.length ? columns : undefined,
      rows: rows.length ? rows : undefined,
    },
  });

  tickets.reload();
}

const filterableFields = createResource({
  url: "helpdesk.api.doc.get_filterable_fields",
  cache: ["DocField", "HD Ticket"],
  auto: true,
  params: {
    doctype: "HD Ticket",
    append_assign: true,
  },
  transform: (data) => {
    return data
      .sort((fieldA, fieldB) => {
        const labelA = fieldA.label.toUpperCase();
        const labelB = fieldB.label.toUpperCase();
        if (labelA < labelB) {
          return -1;
        }
        if (labelA > labelB) {
          return 1;
        }

        return 0;
      })
      .map((field) => {
        return {
          label: field.label,
          value: field.fieldname,
          ...field,
        };
      });
  },
});

const sortableFields = createResource({
  url: "helpdesk.api.doc.sort_options",
  auto: true,
  params: {
    doctype: "HD Ticket",
  },
});

</script>
