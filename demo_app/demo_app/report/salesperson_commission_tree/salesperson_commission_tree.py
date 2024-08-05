# Copyright (c) 2024, ajmal and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


# import frappe

# def get_data(filters):
#     # Fetch sales commissions
#     sales_commissions = frappe.get_all('Sales Commission', fields=['sales_person', 'commission_amount'])
#     print("Sales Commissions:", sales_commissions)
    
#     # Create a dictionary to store commission data by salesperson
#     commission_data = {}
#     for commission in sales_commissions:
#         commission_data[commission['sales_person']] = commission['commission_amount']
#     print("Commission Data:", commission_data)
    
#     # Fetch the hierarchy from Sales Person
#     sales_persons = frappe.get_all('Sales Person', fields=['name', 'parent_sales_person'])
#     print("Sales Persons:", sales_persons)
    
#     # Create a dictionary to represent the tree structure
#     tree_data = {}
#     for person in sales_persons:
#         if person['parent_sales_person'] not in tree_data:
#             tree_data[person['parent_sales_person']] = []
#         tree_data[person['parent_sales_person']].append(person['name'])
#     print("Tree Data:", tree_data)
    
#     return tree_data, commission_data

# def execute(filters=None):
#     data, commission_data = get_data(filters)
    
#     def format_node(node):
#         commission_amount = commission_data.get(node, 0)
#         return {
#             'name': node,
#             'value': commission_amount,
#             'children': [format_node(child) for child in data.get(node, [])]
#         }
    
#     root_nodes = [node for node in data.keys() if node == '']  # Assuming top-level nodes have empty parent_sales_person
#     print("Root Nodes:", root_nodes)
    
#     return [format_node(node) for node in root_nodes]


import frappe

def execute(filters=None):
    data = get_data()
    columns = get_columns()
    return columns, data

@frappe.whitelist()
def get_data():
    sales_persons = get_sales_person_hierarchy()
    commission_data = calculate_commissions(sales_persons)
    
    data = []
    for sales_person in sales_persons:
        data.append({
            'name': sales_person['name'],
            'sales_person': sales_person['name'],
            'parent_sales_person': sales_person['parent_sales_person'],
            'commission_amount': commission_data.get(sales_person['name'], 0)
        })
    return data

def get_sales_person_hierarchy():
    sales_persons = frappe.get_all('Sales Person', fields=['name', 'parent_sales_person', 'is_group'])
    for sales_person in sales_persons:
        commission_amount = frappe.db.get_value('Sales Commission', {'sales_person': sales_person['name']}, 'sum(commission_amount)')
        sales_person['commission_amount'] = commission_amount or 0
    return sales_persons

def calculate_commissions(sales_persons):
    commission_data = {}
    sales_person_dict = {sp['name']: sp for sp in sales_persons}
    
    for sales_person in sales_persons:
        if not sales_person['is_group']:
            calculate_individual_commission(sales_person, sales_person_dict, commission_data)
    
    return commission_data

def calculate_individual_commission(sales_person, sales_person_dict, commission_data):
    commission = sales_person['commission_amount']
    commission_data[sales_person['name']] = commission_data.get(sales_person['name'], 0) + commission
    
    parent = sales_person_dict.get(sales_person['parent_sales_person'])
    if parent:
        if parent['is_group']:
            parent_commission = commission * 0.20
            commission_data[parent['name']] = commission_data.get(parent['name'], 0) + parent_commission
            calculate_individual_commission(parent, sales_person_dict, commission_data)
        
        grandparent = sales_person_dict.get(parent['parent_sales_person'])
        if grandparent and grandparent['is_group']:
            grandparent_commission = commission * 0.30
            commission_data[grandparent['name']] = commission_data.get(grandparent['name'], 0) + grandparent_commission
            calculate_individual_commission(grandparent, sales_person_dict, commission_data)

def get_columns():
    return [
        {"label": "Sales Person", "fieldname": "sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 200},
        {"label": "Parent Sales Person", "fieldname": "parent_sales_person", "fieldtype": "Link", "options": "Sales Person", "width": 200},
        {"label": "Commission Amount", "fieldname": "commission_amount", "fieldtype": "Currency", "width": 150},
    ]
