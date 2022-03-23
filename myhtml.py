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
            (
                f'<input id="{name}" '
                f'type="{type}" '
                f'name="{name}" '
                f'value="{value}" '
                '/><br />'
            )
        )
    
    def text_input(self, label: str, name: str, value: str=''):
        """
        Add a labelled text input element to the form.
        """
        self.__add_label(label, for_=name)
        self.__add_input('text', name, value)

    def number_input(self, label: str, name: str, value: str=''):
        """
        Add a labelled number input element to the form.
        """
        self.__add_label(label, for_=name)
        self.__add_input('number', name, value)

    def date_input(self, label: str, name: str, value: str=''):
        """
        Add a labelled date input element to the form.
        """
        self.__add_label(label, for_=name)
        self.__add_input('date', name, value)

    def email_input(self, label: str, name: str, value: str=''):
        """
        Add a labelled email input element to the form.
        """
        self.__add_label(label, for_=name)
        self.__add_input('email', name, value)

    def password_input(self, label: str, name: str, value: str=''):
        """
        Add a labelled password input element to the form.
        """
        self.__add_label(label, for_=name)
        self.__add_input('password', name, value)

    def hidden_input(self, name: str, value: str=''):
        """
        Add a hidden input element to the form.
        """
        self.__add_input('hidden', name, value)

    def submit_input(self, value: str='Submit'):
        """
        Add a submit input element to the form.
        Input elements are displayed in the order they are added.

        Arguments
        - value: str
          The value attribute used by the element

        Return
        - None
        """
        self.__inputs.append(
            f'<input type="submit" value="{value}" /><br />'
        )

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
        self.__rows = []
        self.headers = kwargs['headers']

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'(headers="{self.headers}")'
        )

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
        self.__rows.append(row)

    def html(self) -> str:
        """
        Generate HTML for the form.
        Each input element has an id that is the same as its name.

        Arguments:
        - None

        Return:
        - str (HTML format)
        """
        html = '<table style="border: 1px solid black;">'
        html += '<tr>'
        for header in self.headers:
            html += f'<th>{header}</th>'
        html += '</tr>'
        for row in self.__rows:
            html += '<tr>'
            for item in row:
                html += f'<td>{item}</td>'
            html += '</tr>'
        html += '</table>'
        
        return html
