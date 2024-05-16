<template>
  <div class="flex flex-col">
    <TicketBreadcrumbs :parent="route.meta.parent" title="New" />
    <div v-if="template.data?.about" class="mx-5 my-3">
      <div class="prose-f" v-html="sanitize(template.data.about)" />
    </div>
    <div class="mx-5 m-5">
      <FormControl
        type="select"
        :options="projectList"
        size="sm"
        variant="subtle"
        placeholder=""
        :disabled="false"
        label="Select Project"
        v-model="project"
    />
    </div>

    <div class="mx-5 mb-5" v-if="employee">
      <FormControl
        type="select"
        :options="departmentList"
        size="sm"
        variant="subtle"
        placeholder=""
        :disabled="false"
        label="Select Department"
        v-model="department"
    />
      
    </div>

    <div class="mx-5 mb-5">
      <FormControl
        v-model="subject"
        type="text"
        label="Subject"
        placeholder="A short description"
      />
    </div>
    
    <div class="mx-5">
      <UniInput
        v-for="field in visibleFields"
        :key="field.fieldname"
        :field="field"
        :value="templateFields[field.fieldname]"
        @change="templateFields[field.fieldname] = $event.value"
      />
      

    </div>
    <TicketNewArticles :search="subject" class="mx-5 mb-5" />
    <span class="mx-5 mb-5">
      <TicketTextEditor
        ref="editor"
        v-model:attachments="attachments"
        v-model:content="description"
        placeholder="Detailed explanation"
        expand
      >
        <template #bottom-right>
          <Button
            label="Submit"
            theme="gray"
            variant="solid"
            :disabled="
              $refs.editor.editor.isEmpty || ticket.loading || !subject || employee && !department || !employee && !project
            "
            @click="() => ticket.submit()"
          />
        </template>
      </TicketTextEditor>
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { createResource, usePageMeta, Button, FormControl, createListResource } from "frappe-ui";
import sanitizeHtml from "sanitize-html";
import { isEmpty } from "lodash";
import { useError } from "@/composables/error";
import { UniInput } from "@/components";
import TicketBreadcrumbs from "./TicketBreadcrumbs.vue";
import TicketNewArticles from "./TicketNewArticles.vue";
import TicketTextEditor from "./TicketTextEditor.vue";


interface P {
  templateId?: string;
}

const props = withDefaults(defineProps<P>(), {
  templateId: "",
});

const route = useRoute();
const router = useRouter();
const subject = ref("");
const description = ref("");
const project = ref("");
const attachments = ref([]);
const templateFields = reactive({});

const projectList = ref([]); // Define project_list
const employee = ref("");
const department = ref("");
const departmentList = ref(["HR", "Technical", "Sales", "Functional"])

createListResource({
  doctype: 'Project',
  url: "helpdesk.helpdesk.doctype.hd_ticket.api.get_projects",
  auto: true,
  onError(error) {
    console.log("Error", error);
  },
  onSuccess(data) {
    projectList.value = data; // Update projectList with the fetched data
  },
});

createListResource({
  doctype: 'Employee',
  url: "helpdesk.helpdesk.doctype.hd_ticket.api.check_is_employee",
  auto: true,
  onError(error) {
    console.log("Error", error);
  },
  onSuccess(data) {
    employee.value = data;
  },
});

const template = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket_template.api.get_one",
  makeParams: () => ({
    name: props.templateId || "Default",
  }),
  auto: true,
});

const visibleFields = computed(() =>
  template.data?.fields?.filter(
    (f) => route.meta.agent || !f.hide_from_customer
  )
);

const ticket = createResource({
  url: "helpdesk.helpdesk.doctype.hd_ticket.api.new",
  debounce: 300,
  makeParams: () => ({
    doc: {
      description: description.value,
      subject: subject.value,
      project: project.value,
      department: department.value,
      template: props.templateId,
      ...templateFields,
    },
    attachments: attachments.value,
  }),

  validate: (params) => {
    const fields = visibleFields.value?.filter((f) => f.required) || [];
    const toVerify = []
    if (employee.value){
      toVerify.push(...fields, "subject", "description", "department")
    }
    else{
      toVerify.push(...fields, "subject", "description", "project")
    }
    
    for (const field of toVerify) {
      if (isEmpty(params.doc[field.fieldname || field])) {
        return `${field.label || field} is required`;
      }
    }
  },
  onSuccess: (data) => {
    router.push({
      name: route.meta.onSuccessRoute as string,
      params: {
        ticketId: data.name,
      },
    });
  },
  onError: useError(),
});

function sanitize(html: string) {
  return sanitizeHtml(html, {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat(["img"]),
  });
}

usePageMeta(() => ({
  title: "New Ticket",
}));
</script>

