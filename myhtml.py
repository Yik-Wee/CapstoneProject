def input_tag(**kwargs):
    attrs = []
    for key, value in kwargs.items():
        if value == False or None:
            continue
        elif value == True:
            attrs.append(key)
        else:
            attrs.append(f'{key}="{value}"')
    attrs = ' '.join(attrs)
    tag = f'<input {attrs}>'
    return tag


def table_input(**kwargs):
    return input_tag(**{'class': 'table-input'}, **kwargs)


class RecordForm:
    """
    Encapsulates data for a form, and contains methods for
    generating an HTML form.

    Form inputs are added with methods.
    Input elements are displayed in the order they are added.

    Available formats:
    - HTML
    """

    def __init__(self, action, method='get'):
        self.__action = action
        self.__method = method
        self.__inputs = []

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'("{self.action()}", method="{self.method()}")'
        )

    def action(self):
        return self.__action

    def method(self):
        return self.__method

    def __add_label(self, label, **kwargs):
        """
        Add a generic label element to the form.

        Arguments
        - label: str
          The label displayed on the form
        - for_: str
          The input tag to label

        Return
        - None
        """
        self.__inputs.append(
            f'<label for="{kwargs.get("for_")}">{label}</label>'
        )

    def __add_input(self, type: str, name: str, value: str):
        """
        Add a generic input element to the form.
        Input elements are displayed in the order they are added.

        Arguments
        - type: str
          The input type
        - name: str
          The name attribute used by the element
        - value: str
          The value attribute used by the element

        Return
        - None
        """
        self.__inputs.append(
            input_tag(id=name, type=type, name=name, value=value) + '<br>')

    def dropdown_input(self, label: str, name: str, options: dict):
        """
        Add a labelled select element to the form. Works as a dropdown menu.
        """
        self.__add_label(label, for_=name)
        html = f'<select name="{name}" id="{name}">'
        for key, value in options.items():
            html += f'<option value="{key}">{value}</option>'
        html += '</select>'
        self.__inputs.append(html)

    def text_input(self, label: str, name: str, value: str = ''):
        """
        Add a labelled text input element to the form.
        """
        self.__add_label(label, for_=name)
        self.__add_input('text', name, value)

    def number_input(self, label: str, name: str, value: str = ''):
        """
        Add a labelled number input element to the form.
        """
        self.__add_label(label, for_=name)
        self.__add_input('number', name, value)

    def date_input(self, label: str, name: str, value: str = ''):
        """
        Add a labelled date input element to the form.
        """
        self.__add_label(label, for_=name)
        self.__add_input('date', name, value)

    def email_input(self, label: str, name: str, value: str = ''):
        """
        Add a labelled email input element to the form.
        """
        self.__add_label(label, for_=name)
        self.__add_input('email', name, value)

    def password_input(self, label: str, name: str, value: str = ''):
        """
        Add a labelled password input element to the form.
        """
        self.__add_label(label, for_=name)
        self.__add_input('password', name, value)

    def hidden_input(self, name: str, value: str = ''):
        """
        Add a hidden input element to the form.
        """
        self.__add_input('hidden', name, value)

    def submit_input(self, value: str = 'Submit'):
        """
        Add a submit input element to the form.
        Input elements are displayed in the order they are added.

        Arguments
        - value: str
          The value attribute used by the element

        Return
        - None
        """
        self.__inputs.append(input_tag(type="submit", value=value) + '<br>')

    def html(self) -> str:
        """
        Generate HTML for the form.
        Each input element has an id that is the same as its name.

        Arguments:
        - None

        Return:
        - str (HTML format)
        """
        html = f'<form action="{self.action()}" method="{self.method()}">'
        for elem_html in self.__inputs:  # elem_html is str
            html += elem_html
        html += '</form>'
        return html


class RecordTable:
    """
    Encapsulates data for a table, and contains methods for
    generating an HTML form.

    Table rows are added with methods.
    Rows are displayed in the order they are added.

    Available formats:
    - HTML
    """

    def __init__(self, **kwargs):
        self._rows = []
        self.headers = kwargs['headers']

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'(headers="{self.headers}")'
        )

    def rows(self):
        return self._rows

    def add_row(self, data: dict):
        """
        Add a row to the table from data.
        Data keys must match table headers.

        Arguments
        - data: dict
          The row to be added to the table.

        Return
        - None
        """
        row = []
        for key in self.headers:
            row.append(data[key])
        self._rows.append(row)

    def html(self) -> str:
        """
        Generate HTML for the form.
        Each input element has an id that is the same as its name.

        Arguments:
        - None

        Return:
        - str (HTML format)
        """
        html = '<table>'
        html += '<tr>'
        for header in self.headers:
            html += f'<th>{header}</th>'
        html += '</tr>'
        for row in self._rows:
            html += '<tr>'
            for item in row:
                html += f'<td>{item}</td>'
            html += '</tr>'
        html += '</table>'

        return html


class RecordTableForm(RecordTable):
    def __init__(self, **kwargs):
        """
        Arguments:
        - action: str
          The action for each row's form element. Default ''
        - method: str
          The method for each row's form element ('get' | 'post'). Default 'get'
        - headers: list
          The headers/columns of the table
        - search_by: str
          The records to filter/search by, specified in the request parameters. Default None
        - form_id: str
          The `id` of the form to be used. Default 'table-form'
        """
        self.__action = kwargs.get('action', '')
        self.__method = kwargs.get('method', 'get')
        self.__search_by = kwargs.get('search_by')
        self.form_id = kwargs.get('form_id', 'table-form')
        super().__init__(**kwargs)

    def action(self):
        return self.__action

    def method(self):
        return self.__method

    def search_by(self):
        return self.__search_by
    
    def _gen_headers_html(self) -> str:
        """Generate the headers of the table within a `<tr>` tag"""
        html = '<tr>'
        for header in self.headers:
            html += f'<th>{header}</th>'
        html += '</tr>'
        return html


class SelectableRecordTable(RecordTableForm):
    """
    Display an html RecordTable that allows the user to click & choose a row/record
    which redirects them to `self.action()` with the method `self.method()`, with the
    record as the request parameters.
    """

    def html(self) -> str:
        html = '<table>'
        html += self._gen_headers_html()
        for row in self.rows():
            html += '<tr>'
            html += f'<form action="{self.action()}" method="{self.method()}">'
            for idx, item in enumerate(row):
                header = self.headers[idx]
                html += f'''<td>
                    {table_input(type="hidden", name=header, value=item)}
                    {item}
                    </td>'''
            html += '<td>'
            html += table_input(type="submit", value="🤏 Choose Record")
            if self.search_by() is not None:
                html += table_input(type="hidden", name="search_by", value=self.search_by())
            html += '</td>'
            html += '</form>'
            html += '</tr>'
        html += '</table>'

        return html


class EditableRecordTable(RecordTableForm):
    """
    Display an html RecordTable with the ability to edit each rows/record's fields.
    """
    def __init__(self, **kwargs):
        """
        Arguments:
        - action: str
          The action for each row's form element. Default '' (empty str)
        - method: str
          The method for each row's form element ('get' | 'post'). Default 'get'
        - headers: list
          The headers/columns of the table
        - header_types: dict
          the input types for the table's headers
          (see `set_header_types()`)
        - search_by: str
          The records to filter/search by, specified in the request parameters. Default None
        - filter: dict
          The filter to search the records by
        """
        self.__filter = kwargs.get('filter')
        header_types = kwargs.get('header_types', {})
        self.set_header_types(header_types)
        super().__init__(**kwargs)

    def set_header_types(self, header_types: dict):
        """
        Set the `header_types` for the table headers. e.g.
        ```py
        {
            'name': data.String,
            'year': data.Year,
            'date': data.Date,
            ...
        }
        ```
        """
        self.__header_types = header_types

    def html(self) -> str:
        html = f'<form action="{self.action()}" method="{self.method()}" id="{self.form_id}"></form>'
        html += '<table>'
        html += self._gen_headers_html()
        for row in self.rows():
            html += '<tr>'
            for idx, item in enumerate(row):
                header = self.headers[idx]
                header_type = self.__header_types[header]
                html += f'''<td>
                    {table_input(type="hidden", name="old:"+header, value=item, form=self.form_id)}
                    {table_input(type=header_type, name="new:"+header, value=item, form=self.form_id)}
                    </td>'''
            html += f'''<td>
                <select id="method" name="method" form="{self.form_id}">
                    <option value="UPDATE">Update</option>
                    <option value="DELETE">Delete</option>
                </select>
                </td>'''
            html += '</tr>'
        html += '</table>'
        if self.search_by() is not None:
            html += table_input(type="hidden", name="search_by", value=self.search_by(), form=self.form_id)
        if self.__filter is not None:
            for key, value in self.__filter.items():
                html += table_input(type="hidden", name="filter:"+key, value=value, form=self.form_id)
        html += table_input(type="submit", value="Save Changes", form=self.form_id)

        return html


class SubmittableRecordTable(RecordTableForm):
    def __init__(self, **kwargs):
        """
        Arguments:
        - action: str
          The action for each row's form element. Default '' (empty str)
        - method: str
          The method for each row's form element ('get' | 'post'). Default 'get'
        - headers: list
          The headers/columns of the table
        - search_by: str
          The records to filter/search by, specified in the request parameters. Default None
        - filter: dict
          The filter to search by
        """
        self.__filter = kwargs.get('filter')
        super().__init__(**kwargs)

    def add_row(self, old_data: dict, new_data: dict, method: str):
        old_rows = []
        new_rows = []
        for key in self.headers:
            old_rows.append(old_data[key])
            new_rows.append(new_data[key])
        self._rows.append({'old': old_rows, 'new': new_rows, 'method': method})

    def html(self) -> str:
        html = f'<form action="{self.action()}" method="{self.method()}" id="{self.form_id}"></form>'
        html += '<table>'
        html += self._gen_headers_html()
        for row in self.rows():
            method = row['method']
            html += f'<tr class="tr-{method.lower()}">'
            for i, new_item in enumerate(row['new']):
                old_item = row['old'][i]
                header = self.headers[i]
                if method == 'DELETE':  # strikethrough to show deleted
                    new_item_display = f'🗑️<s>{old_item}</s>'
                else:
                    new_item_display = new_item
                
                html += f'''<td>
                    {table_input(type="hidden", name="old:"+header, value=old_item, form=self.form_id)}
                    {table_input(type="hidden", name="new:"+header, value=new_item, form=self.form_id)}
                    {new_item_display}
                    </td>'''
            html += f'''<td class="td-hide">
                {table_input(type="hidden", name="method", value=method, form=self.form_id)}
                </td>'''
            html += '</tr>'
        html += '</table>'
        if self.search_by() is not None:
            html += table_input(type="hidden", name="search_by", value=self.search_by(), form=self.form_id)
        if self.__filter is not None:
            for key, value in self.__filter.items():
                html += table_input(type="hidden", name="filter:"+key, value=value, form=self.form_id)

        html += table_input(type="submit", value="Save Changes", form=self.form_id)

        return html
