# Project: blog_7myon_com
# Package: 
# Filename: form_helpers.py
# Generated: 2021 Jan 01 at 10:31 
# Description of <form_helpers>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>

def get_widget_data_from_form(form, include_hidden=False):
    """
        Returns list of 2-tuples where value under 0 index is field's labels
        and value under 0 index is lists of text data.
        If form contains multi select widget then will be returned list of text that selected.
    """
    form_data = []
    for bfield in form:
        if not include_hidden and bfield.is_hidden:
            continue
        values = []
        for subwidg in bfield:
            value = subwidg.data['value']
            if 'selected' in subwidg.data:
                if not subwidg.data['selected']:
                    continue
                else:
                    value = subwidg.data['label']

            if subwidg.data.get('type') in ('checkbox', 'radio'):
                value = subwidg.data['attrs'].get('checked', False)

            values.append(value)
        form_data.append((bfield.label, values))

    return form_data


def get_widgets_data_from_formset(formset, include_hidden=False):
    """
    Returns list of the 2-tuple value where each element is result of get_widget_data_from_form(...)

    :param formset: Iterable where each item is Form or ModelForm if
        ModelForm then key of resulted dictionary will contain the value of primary key
    :param include_hidden: Boolean value. If False (by default) then will not be included in result
    :return: List of the 2-tuple value where each element is result of get_widget_data_from_form(...)
    """
    pk_name = None
    data = []
    for idx, _form in enumerate(formset):
        if idx == 0:
            # Each ModelForm has _meta.model attribute. We try to recognize the duck
            opts = getattr(_form, '_meta', False)
            if opts and getattr(opts, 'model', False):
                pk_name = opts.model._meta.pk.name

        if not pk_name:
            td = _form.data if _form.is_bound else _form.initial
            if 'id' in td:
                pk_value = td['id']
        else:
            pk_value = _form[pk_name].value() if pk_name else idx

        form_data = get_widget_data_from_form(_form, include_hidden)
        data.append((pk_value, form_data))
    return data
