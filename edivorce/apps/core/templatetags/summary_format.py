from collections import OrderedDict

from django import template
import json

register = template.Library()


@register.simple_tag
def reformat_value(source, question_key):
    """
    Reformat user response on summary page
    ie) Remove [], make it a bullet point form
    """
    try:
        lst = json.loads(source)
        if len(lst) == 1:
            return lst[0]
        else:
            return process_list(lst, question_key)
    except:
        if question_key == 'spouse_support_details' or question_key == 'other_orders_detail'\
                or question_key == 'provide_certificate_later_reason' or question_key == 'not_provide_certificate_reason':
            text_list = source.split('\n')
            tag = ["<ul>"]
            for value in text_list:
                if value and not value.isspace():
                    tag.append('<li>' + value + '</li>')
            tag.append('</ul>')
            return ''.join(tag)
        return source


def process_list(lst, question_key):
    tag = ["<ul>"]
    if question_key.startswith('other_name_'):
        for alias_type, value in lst:
            if value:
                tag.append('<li>' + alias_type + ' ' + value + '</li>')
    else:
        for value in lst:
            if value and not value.isspace():
                tag.append('<li>' + str(value) + '</li>')
    tag.append('</ul>')
    return ''.join(tag)


def format_row(question, response):
    return '<tr><td width="75%" style="padding-right: 5%">{0}</td><td width="25%">{1}</td></tr>'.format(
        question, response
    )


def format_head(headings):
    if len(headings) == 0:
        return '', []

    tags = ["<tr>"]
    head_order = list()
    for key in headings[0].keys():
        tags.append('<th>{}</th>'.format(key.replace('_', ' ').title()))
        head_order.append(key)
    tags.append('</tr>')
    return ''.join(tags), head_order


def process_fact_sheet_list(data, header):
    tags = list()
    for item in data:
        tags.append('<tr>')
        for key in header:
            tags.append('<td>{}</td>'.format(item.get(key, '')))
        tags.append('</tr>')
    return ''.join(tags)


def format_fact_sheet(title, responses):
    if len(responses) == 0:
        return ''

    tags = ['<tr><td colspan="2">']
    tags.append('<h3>{}</h3>'.format(title))

    for response in responses:
        value = response['value']
        try:
            value = json.loads(response['value'])
        except:
            pass

        if not value:
            continue

        if isinstance(value, list):
            thead, header = format_head(value)
            tags.append("""
                <p></p>
                <p><strong>{0}</strong></p>
                <table class="table table-bordered table-striped">
                <thead>
                    {1}
                </thead>
                <tbody>
            """.format(response['question__name'], thead))

            tags.append(process_fact_sheet_list(value, header))
        else:
            tags.append("""
            <table class="table table-bordered table-striped">
                <thead>
                    <th></th>
                    <th></th>
                </thead>
                <tbody>
            """)
            tags.append(format_row(response['question__name'], value))
        tags.append("""
            </tbody>
            </table>
            """)
    tags.append('</td></tr>')
    return ''.join(tags)


@register.simple_tag(takes_context=True)
def format_children(context, source):
    """

    :param source:
    :return:
    """
    question_to_heading = OrderedDict()
    question_to_heading['Your Children'] = [
        'claimant_children'
    ]
    question_to_heading['What are you asking for?'] = [
        'have_separation_agreement',
        'have_court_order',
        'order_respecting_arrangement',
        'order_for_child_support',
        'child_support_act'
    ]
    question_to_heading['Income & expenses'] = [
        'how_will_calculate_income',
        'annual_gross_income',
        'spouse_annual_gross_income'
    ]
    question_to_heading['Are you or your spouse claiming undue hardship?'] = [
        'special_extraordinary_expenses',
        'claiming_undue_hardship',
        'Undue Hardship (Fact Sheet E)'
    ]
    question_to_heading['Payor & medical expenses'] = [
        'child_support_payor',
        'claimants_agree_to_child_support_amount',
        'medical_coverage_available',
        'child_support_payments_in_arrears'
    ]
    question_to_heading['Other fact sheets'] = [
        'Special or Extraordinary Expenses (Fact Sheet A)',
        'Shared Living Arrangement (Fact Sheet B)',
        'Split Living Arrangement (Fact Sheet C)',
        'Child(ren) 19 Years or Older (Fact Sheet D)',
        'Income over $150,000 (Fact Sheet F)'
    ]

    fact_sheet_mapping = OrderedDict()
    fact_sheet_mapping['Special or Extraordinary Expenses (Fact Sheet A)'] = [
        'child_care_expenses',
        'children_healthcare_premiums',
        'health_related_expenses',
        'extraordinary_educational_expenses',
        'post_secondary_expenses',
        'extraordinary_extracurricular_expenses',
        'total_section_seven_expenses',
        'your_proportionate_share_percent',
        'your_proportionate_share_amount',
        'spouse_proportionate_share_percent',
        'spouse_proportionate_share_amount'
    ]
    fact_sheet_mapping['Shared Living Arrangement (Fact Sheet B)'] = [
        'number_of_children',
        'time_spent_with_you',
        'time_spent_with_spouse',
        'annual_gross_income',
        'spouse_annual_gross_income',
        'your_child_support_paid',
        'your_spouse_child_support_paid',
        'extra_ordinary_expenses_you',
        'extra_ordinary_expenses_spouse',
        'additional_relevant_spouse_children_info',
        'difference_between_claimants'
    ]
    fact_sheet_mapping['Split Living Arrangement (Fact Sheet C)'] = [
        'number_of_children_claimant',
        'spouse_annual_gross_income',
        'total_spouse_paid_child_support',
        'annual_gross_income',
        'total_paid_child_support'
        'difference_payment_amounts'
    ]
    fact_sheet_mapping['Child(ren) 19 Years or Older (Fact Sheet D)'] = [
        'number_children_over_19_need_support',
        'total_spouse_paid_child_support',
        'agree_to_child_support_amount',
        'total_spouse_paid_child_support',
        'suggested_child_support'
    ]
    fact_sheet_mapping['Undue Hardship (Fact Sheet E)'] = [
        'claimant_debts',
        'claimant_expenses',
        'supporting_non_dependents',
        'supporting_dependents',
        'supporting_disabled',
        'undue_hardship',
        'income_others',
        'total_income_others'
    ]
    fact_sheet_mapping['Income over $150,000 (Fact Sheet F)'] = [
        'number_children_seeking_support',
        'child_support_amount_under_high_income',
        'percent_income_over_high_income_limit',
        'amount_income_over_high_income_limit',
        'total_guideline_amount',
        'agree_to_child_support_amount',
        'reason_child_support_amount'
    ]

    tags = []
    # process mapped questions first
    working_source = source.copy()
    for title, questions in question_to_heading.items():
        tags.append(format_row('<strong>{}</strong>'.format(title), ''))

        for question in questions:
            if question in fact_sheet_mapping:
                show_fact_sheet = False
                if question == 'Special or Extraordinary Expenses (Fact Sheet A)' and context['derived']['show_fact_sheet_a']:
                    show_fact_sheet = True
                elif question == 'Shared Living Arrangement (Fact Sheet B)' and context['derived']['show_fact_sheet_b']:
                    show_fact_sheet = True
                elif question == 'Split Living Arrangement (Fact Sheet C)' and context['derived']['show_fact_sheet_c']:
                    show_fact_sheet = True
                elif question == 'Child(ren) 19 Years or Older (Fact Sheet D)' and context['derived']['show_fact_sheet_d']:
                    show_fact_sheet = True
                elif question == 'Undue Hardship (Fact Sheet E)' and context['derived']['show_fact_sheet_e']:
                    show_fact_sheet = True
                elif question == 'Income over $150,000 (Fact Sheet F)' and context['derived']['show_fact_sheet_f']:
                    show_fact_sheet = True

                if show_fact_sheet and len(fact_sheet_mapping[question]):
                    responses = list(filter(lambda x: x['question_id'] in fact_sheet_mapping[question], working_source))
                    tags.append(format_fact_sheet(question, responses))
            else:
                item = list(filter(lambda x: x['question_id'] == question, working_source))

                if len(item):
                    item = item.pop()
                    q_id = item['question_id']
                    if q_id in questions:
                        if q_id == 'claimant_children':
                            for child in json.loads(item['value']):
                                tags.append(format_row('Child\'s name', child['child_name']))
                                tags.append(format_row('Birth date', child['child_birth_date']))
                                tags.append(format_row('Child living with', child['child_live_with']))
                                tags.append(format_row('Relationship to yourself (claimant 1)', child['child_relationship_to_you']))
                                tags.append(format_row('Relationship to your spouse (claimant 2)', child['child_relationship_to_spouse']))
                        else:
                            value = item['value']
                            try:
                                value = json.loads(item['value'])
                            except:
                                pass
                            if isinstance(value, list):
                                tags.append(format_row(item['question__name'], process_list(value, q_id)))
                            else:
                                tags.append(format_row(item['question__name'], value))
    return ''.join(tags)


@register.simple_tag
def combine_address(source):
    """
        Reformat address to combine them into one cell with multiple line
        Also show/hide optional questions
    """
    tags = []
    first_column = '<tr><td width="75%" style="padding-right: 5%">'
    second_column = '<td width="25%">'
    end_tag = '</td></tr>'

    address_you = ""
    fax_you = ""
    email_you = ""
    address_spouse = ""
    fax_spouse = ""
    email_spouse = ""
    is_specific_date = False
    effective_date = ""

    for item in source:
        q_id = item['question_id']
        if "you" in q_id:
            if "email" not in q_id and "fax" not in q_id:
                if q_id == "address_to_send_official_document_country_you":
                    continue
                address_you += item["value"] + '<br />'
            elif "fax" in q_id:
                fax_you = item["value"]
            elif "email" in q_id:
                email_you = item["value"]
        elif "spouse" in q_id:
            if "email" not in q_id and "fax" not in q_id:
                if q_id == "address_to_send_official_document_country_spouse":
                    continue
                address_spouse += item["value"] + '<br />'
            elif "fax" in q_id:
                fax_spouse = item["value"]
            elif "email" in q_id:
                email_spouse = item["value"]
        elif q_id == "divorce_take_effect_on":
            if item['value'] == "specific date":
                is_specific_date = True
            else:
                effective_date = item['value']
        elif q_id == "divorce_take_effect_on_specific_date" and is_specific_date:
            effective_date = item['value']

    if address_you != "":
        tags.append(first_column + "What is the best address to send you official court documents?</td>"
                    + second_column + address_you + end_tag)
    if fax_you != "":
        tags.append(first_column + "Fax</td>" + second_column + fax_you + end_tag)

    if email_you != "":
        tags.append(first_column + "Email</td>" + second_column + email_you + end_tag)

    if address_spouse != "":
        tags.append(first_column + "What is the best address to send your spouse official court documents?</td>"
                    + second_column + address_spouse + end_tag)
    if fax_spouse != "":
        tags.append(first_column + "Fax</td>" + second_column + fax_spouse + end_tag)

    if email_spouse != "":
        tags.append(first_column + "Email</td>" + second_column + email_spouse + end_tag)

    if effective_date != "":
        tags.append(first_column + "Divorce is to take effect on </td>" + second_column + effective_date + end_tag)

    return ''.join(tags)


@register.simple_tag(takes_context=True)
def marriage_tag(context, source):
    """
        Reformat your_marriage step
        Also show/hide optional questions
    """
    show_all = False
    tags = []
    first_column = '<tr><td width="75%" style="padding-right: 5%">'
    second_column = '</td><td width="25%">'
    end_tag = '</td></tr>'

    marriage_location = ""
    married_date = ""
    married_date_q = ""
    common_law_date = ""
    common_law_date_q = ""
    marital_status_you = ""
    marital_status_you_q = ""
    marital_status_spouse = ""
    marital_status_spouse_q = ""

    # get married_marriage_like value to check if legally married or not
    for question in context.get('prequalification', ''):
        if question['question_id'] == 'married_marriage_like' and question['value'] == 'Legally married':
            show_all = True
            break
        elif question['question_id'] == 'married_marriage_like':
            break

    for item in source:
        q_id = item['question_id']
        value = item['value']
        q_name = item['question__name']

        if q_id == 'when_were_you_married':
            married_date_q = q_name
            married_date = value
        elif q_id == 'when_were_you_live_married_like':
            common_law_date_q = q_name
            common_law_date = value
        elif q_id.startswith('where_were_you_married'):
            if value == 'Other':
                continue
            marriage_location += value + '<br />'
        elif q_id == 'marital_status_before_you':
            marital_status_you_q = q_name
            marital_status_you = value
        elif q_id == 'marital_status_before_spouse':
            marital_status_spouse_q = q_name
            marital_status_spouse = value

    if show_all and married_date != "":
        tags.append(first_column + married_date_q + second_column + married_date + end_tag)
    if common_law_date != "":
        tags.append(first_column + common_law_date_q + second_column + common_law_date + end_tag)
    if show_all and marriage_location != "":
        tags.append(first_column + "Where were you married" + second_column + marriage_location + end_tag)
    if marital_status_you != "":
        tags.append(first_column + marital_status_you_q + second_column + marital_status_you + end_tag)
    if marital_status_spouse != "":
        tags.append(first_column + marital_status_spouse_q + second_column + marital_status_spouse + end_tag)

    return ''.join(tags)


@register.simple_tag
def property_tag(source):
    """
        Reformat your_property and debt step
        Also show/hide optional questions
    """
    tags = []
    first_column = '<tr><td width="75%" style="padding-right: 5%">'
    second_column = '</td><td width="25%">'
    end_tag = '</td></tr>'

    division = division_detail = other_detail = None

    for item in source:
        q_id = item['question_id']

        if q_id == 'deal_with_property_debt':
            division = item
        elif q_id == 'how_to_divide_property_debt':
            division_detail = item
        elif q_id == 'other_property_claims':
            other_detail = item

    if division:
        tags.append(first_column + division['question__name'] + second_column + division['value'] + end_tag)
    if division and division['value'] == "Unequal division" and division_detail:
        tags.append(first_column + division_detail['question__name'] + second_column + process_list(division_detail['value'].split('\n'), division_detail['question_id']) + end_tag)
    if other_detail and other_detail['value'].strip():
        tags.append(first_column + other_detail['question__name'] + second_column + process_list(other_detail['value'].split('\n'), other_detail['question_id']) + end_tag)

    return ''.join(tags)


@register.simple_tag
def prequal_tag(source):
    """
        Reformat prequalification step
        Also show/hide optional questions
    """
    tags = []
    first_column = '<tr><td width="75%" style="padding-right: 5%">'
    second_column = '</td><td width="25%">'
    end_tag = '</td></tr>'

    marriage_status = lived_in_bc = live_at_least_year = separation_date = try_reconcile = reconciliation_period = None
    children_of_marriage = number_children_under_19 = number_children_over_19 = financial_support = certificate = provide_later = None
    provide_later_reason = not_provide_later_reason = in_english = divorce_reason = None

    for item in source:
        q_id = item['question_id']
        if q_id == 'married_marriage_like':
            marriage_status = item
        elif q_id == 'lived_in_bc':
            lived_in_bc = item
        elif q_id == 'lived_in_bc_at_least_year':
            live_at_least_year = item
        elif q_id == 'separation_date':
            separation_date = item
        elif q_id == 'try_reconcile_after_separated':
            try_reconcile = item
        elif q_id == 'reconciliation_period':
            reconciliation_period = item
        elif q_id == 'children_of_marriage':
            children_of_marriage = item
        elif q_id == 'number_children_under_19':
            number_children_under_19 = item
        elif q_id == 'number_children_over_19':
            number_children_over_19 = item
        elif q_id == 'children_financial_support':
            financial_support = item
        elif q_id == 'original_marriage_certificate':
            certificate = item
        elif q_id == 'provide_certificate_later':
            provide_later = item
        elif q_id == 'provide_certificate_later_reason':
            provide_later_reason = item
        elif q_id == 'not_provide_certificate_reason':
            not_provide_later_reason = item
        elif q_id == 'marriage_certificate_in_english':
            in_english = item
        elif q_id == 'divorce_reason':
            divorce_reason = item
            if divorce_reason['value'] == 'live separate':
                divorce_reason['value'] = 'Lived apart for one year'

    if marriage_status:
        tags.append(first_column + marriage_status['question__name'] + second_column + marriage_status['value'] + end_tag)
    if lived_in_bc:
        tags.append(first_column + lived_in_bc['question__name'] + second_column + lived_in_bc['value'] + end_tag)
    if live_at_least_year:
        tags.append(first_column + live_at_least_year['question__name'] + second_column + live_at_least_year['value'] + end_tag)
    if separation_date:
        tags.append(first_column + separation_date['question__name'] + second_column + separation_date['value'] + end_tag)
    if try_reconcile:
        tags.append(first_column + try_reconcile['question__name'] + second_column + try_reconcile['value'] + end_tag)
    if try_reconcile and try_reconcile['value'] == 'YES' and reconciliation_period:
        tags.append(first_column + reconciliation_period['question__name'] + second_column + reconciliation_period_reformat(reconciliation_period['value']) + end_tag)
    if children_of_marriage:
        tags.append(first_column + children_of_marriage['question__name'] + second_column + children_of_marriage['value'] + end_tag)
    if children_of_marriage and children_of_marriage['value'] == 'YES' and number_children_under_19:
        tags.append(first_column + number_children_under_19['question__name'] + second_column + number_children_under_19['value'] + end_tag)
    if children_of_marriage and children_of_marriage['value'] == 'YES' and number_children_over_19:
        tags.append(first_column + number_children_over_19['question__name'] + second_column + number_children_over_19['value'] + end_tag)
    if children_of_marriage and children_of_marriage['value'] == 'YES' and number_children_over_19 and financial_support and financial_support['value']:
        tags.append(first_column + financial_support['question__name'] + second_column + '<br>'.join(json.loads(financial_support['value'])) + end_tag)
    if certificate:
        tags.append(first_column + certificate['question__name'] + second_column + certificate['value'] + end_tag)
    if certificate and certificate['value'] == 'NO' and provide_later:
        tags.append(first_column + provide_later['question__name'] + second_column + provide_later['value'] + end_tag)
    if certificate and provide_later and certificate['value'] == 'NO' and provide_later['value'] == 'YES' and provide_later_reason:
        tags.append(first_column + provide_later_reason['question__name'] + second_column + process_list(provide_later_reason['value'].split('\n'), provide_later_reason['question_id']) + end_tag)
    if certificate and provide_later and certificate['value'] == 'NO' and provide_later['value'] == 'NO' and not_provide_later_reason:
        tags.append(first_column + not_provide_later_reason['question__name'] + second_column + process_list(not_provide_later_reason['value'].split('\n'), not_provide_later_reason['question_id']) + end_tag)
    if marriage_status and marriage_status['value'] == 'Living together in a marriage like relationship' and in_english:
        tags.append(first_column + in_english['question__name'] + second_column + in_english['value'] + end_tag)
    if divorce_reason:
        tags.append(first_column + divorce_reason['question__name'] + second_column + divorce_reason['value'] + end_tag)

    return ''.join(tags)


@register.simple_tag
def personal_info_tag(source):
    """
        Reformat your information and your spouse step
        Also show/hide optional questions
    """
    tags = []
    first_column = '<tr><td width="75%" style="padding-right: 5%">'
    second_column = '</td><td width="25%">'
    end_tag = '</td></tr>'

    name = other_name = other_name_list = last_name_born = last_name_before = None
    birthday = occupation = lived_bc = moved_bc = None

    for item in source:
        q_id = item['question_id']

        if q_id.startswith('name_'):
            name = item
        elif q_id.startswith('any_other_name_'):
            other_name = item
        elif q_id.startswith('other_name_'):
            other_name_list = item
        elif q_id.startswith('last_name_born_'):
            last_name_born = item
        elif q_id.startswith('last_name_before_married_'):
            last_name_before = item
        elif q_id.startswith('birthday_'):
            birthday = item
        elif q_id.startswith('occupation_'):
            occupation = item
        elif q_id.startswith('lived_in_bc_'):
            lived_bc = item
        elif q_id.startswith('moved_to_bc_date_'):
            moved_bc = item

    if name:
        tags.append(first_column + name['question__name'] + second_column + name['value'] + end_tag)
    if other_name:
        tags.append(first_column + other_name['question__name'] + second_column + other_name['value'] + end_tag)
    if other_name and other_name['value'] == 'YES' and other_name_list:
        tags.append(first_column + other_name_list['question__name'] + second_column + process_list(json.loads(other_name_list['value']), other_name_list['question_id']) + end_tag)
    if last_name_born:
        tags.append(first_column + last_name_born['question__name'] + second_column + last_name_born['value'] + end_tag)
    if last_name_before:
        tags.append(first_column + last_name_before['question__name'] + second_column + last_name_before['value'] + end_tag)
    if birthday:
        tags.append(first_column + birthday['question__name'] + second_column + birthday['value'] + end_tag)
    if occupation:
        tags.append(first_column + occupation['question__name'] + second_column + occupation['value'] + end_tag)
    if lived_bc and moved_bc and lived_bc['value'] == "Moved to B.C. on":
        tags.append(first_column + lived_bc['question__name'] + second_column + lived_bc['value'] + ' ' + moved_bc['value'] + end_tag)
    if lived_bc and lived_bc['value'] != "Moved to B.C. on" and lived_bc:
        tags.append(first_column + lived_bc['question__name'] + second_column + lived_bc['value'] + end_tag)

    return ''.join(tags)


def reconciliation_period_reformat(lst):
    """
        Reformat reconciliation period into From [dd/mm/yyyy] to [dd/mm/yyyy] format
    """
    try:
        lst = json.loads(lst)
    except:
        lst = []
    period = ""
    for f_date, t_date in lst:
        period += "From " + f_date + " to " + t_date + "<br />"
    return period
