import frappe

def set_employee_based_on_assignment(doc, method):
    if doc.reference_type == "HD Ticket":
        sub_assign = frappe.db.get_value("HD Sub Team", filters={"member": doc.allocated_to}, fieldname="name")
        frappe.db.set_value("HD Ticket", doc.reference_name, "assign_employee", sub_assign)
        frappe.db.commit()
        