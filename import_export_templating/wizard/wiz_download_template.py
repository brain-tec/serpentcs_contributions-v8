# See LICENSE file for full copyright and licensing details.

import base64
import tempfile
from datetime import datetime
from io import BytesIO

import xlwt
from xlrd import open_workbook

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import misc


class WizDownloadTemplate(models.TransientModel):
    _name = "wiz.download.template"
    _rec_name = "ir_model"
    _description = "Wiz Download Template"

    @api.depends("ir_model", "ir_model.field_id", "ir_model.field_id.model_id")
    def _compute_get_names(self):
        self.field_names_computed = self.ir_model.field_id.filtered(
            lambda l: l.model_id.id == self.ir_model.id
        )

    type = fields.Selection([("export", "Export"), ("import", "Import")], string="Type")
    ir_model = fields.Many2one("ir.model", string="Select Type Of Document To Download")
    upload_file = fields.Binary(string="Upload File")
    fname = fields.Char("File Name")
    create_m2o = fields.Boolean(string="Create Many2one")
    create_m2m = fields.Boolean(string="Create Many2many")
    update_only = fields.Boolean(string="Update records", default=True)
    create_only = fields.Boolean(string="Create records", default=True)
    field_names_computed = fields.Many2many(
        "ir.model.fields", compute="_compute_get_names"
    )
    fields_list_ids = fields.Many2many(
        "ir.model.fields", domain="[('model_id', '=', ir_model)]"
    )

    @api.onchange("type")
    def _get_active_model(self):
        model = self._context.get("active_model")
        if model:
            ir_model = self.env["ir.model"].search([("model", "=", model)])
            self.ir_model = ir_model.id
            return {"domain": {"ir_model": [("id", "=", ir_model.id)]}}

    @api.onchange("ir_model")
    def _onchange_blank(self):
        self.button_uncheck()

    def button_required(self):
        manual_selected = []
        if self.fields_list_ids:
            manual_selected.extend(self.fields_list_ids.ids)

        required = []
        required.extend(self.field_names_computed.filtered(lambda l: l.required).ids)

        self.fields_list_ids = manual_selected + required
        ctx = dict(self._context)
        ctx.update({"nodestroy": False})
        return {
            "context": ctx,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wiz.download.template",
            "res_id": self.id,
            "view_id": False,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def button_select_all(self):
        self.fields_list_ids = [
            (6, 0, self.field_names_computed.filtered(lambda l: l.name != "id").ids)
        ]
        ctx = dict(self._context)
        ctx.update({"nodestroy": False})
        return {
            "context": ctx,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wiz.download.template",
            "res_id": self.id,
            "view_id": False,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def button_uncheck(self):
        self.fields_list_ids = [(5, self.field_names_computed.ids)]
        ctx = dict(self._context)
        ctx.update({"nodestroy": False})
        return {
            "context": ctx,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wiz.download.template",
            "res_id": self.id,
            "view_id": False,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def download_template(self, row_values=None, error_reason=None, error_value=None):
        """This method is used for export template."""
        fl = BytesIO()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(self.ir_model.name)

        bold = xlwt.easyxf("font: bold 1;")
        main_header = xlwt.easyxf(
            "font: bold 1, height 270;"
            " align: horiz center,vert center,wrap 1;"
            "borders: top hair, bottom hair, left hair, right hair, "
            "bottom_color black, top_color black"
        )
        label_header = xlwt.easyxf(
            "font: bold 1, height 230;"
            " align: horiz center,vert center,wrap 1;"
            "borders: top hair, bottom hair, left hair, right hair, "
            "bottom_color black, top_color black"
        )

        row_start = 12
        col_width = 9500
        max_col = 5
        column_headers = ["Column Name:", "Type:", "Mandatory:", "Column Labels:"]
        row_indices = list(range(row_start, row_start + len(column_headers)))

        worksheet.row(0).height = 500
        for col in range(max_col):
            worksheet.col(col).width = col_width if col > 0 else 6200

        worksheet.write_merge(0, 0, 0, max_col - 1, "Data Import Template", main_header)

        def merge_cells(row, col_start, col_end, value, style=None):
            """Helper function to merge cells with a given style."""
            if style is None:
                style = xlwt.easyxf("font: ")
            worksheet.write_merge(row, row, col_start, col_end, value, style)

        # Notes section
        for row in range(1, 3):
            worksheet.write_merge(row, row, 0, 4, "")
        worksheet.write_merge(3, 3, 0, 2, "Notes:", bold)
        notes = [
            "Please do not change the template headings.",
            "First data column must be blank.",
            'If you are uploading new records, "Naming Series" becomes mandatory, if present.',
            "Only mandatory fields are necessary for new records. You can keep non-mandatory columns blank if you wish.",
            "For updating, you can update only selective columns.",
            "You can only upload upto 5000 records in one go. (may be less in some cases)",
        ]
        for idx, note in enumerate(notes, start=4):
            worksheet.write_merge(idx, idx, 0, 2, note)

        import_notes = [
        'Many2one: You can enter "NAME" of the relational model!',
        'Many2many: You can enter "Name" of the relational model, separate by ";"',
        "One2many: Let this blank! & Download Blank Template for displayed comodel to Import!",
        "There should only be one required field in relational model for creation of new record.",
        ]
        merge_cells(3, 3, 4, "Data Import Notes:", bold)
        for i, note in enumerate(import_notes, start=5):
            merge_cells(i, 3, 4, note)

        labels = ["DocType:", *column_headers, "Start entering data this line"]
        worksheet.write(12, 1, self.ir_model.model)
        default_style = xlwt.easyxf("font: height 230; align: horiz left, vert center")
        for idx, label in enumerate(labels):
            worksheet.write(row_start + idx, 0, label, bold if idx < 2 or idx == len(labels) - 1 else default_style)

        if not self.fields_list_ids and not error_value:
            raise UserError(_("Fields should not be blank!"))

        if self.fields_list_ids:
            for col_idx, field in enumerate(self.fields_list_ids, start=1):
                worksheet.col(col_idx).width = col_width
                worksheet.write(row_start + 1, col_idx, field.name)
                field_info = f"{field.ttype} Relation: {field.relation}" if field.relation else field.ttype
                worksheet.write(row_start + 2, col_idx, field_info)

                is_delegated = (
                        (field.ttype == "many2one" and field.relation in [x.model for x in
                                                                          self.ir_model.inherited_model_ids] and not field.related)
                        or field.ttype == "one2many"
                )
                is_required = "Yes" if field.required and not is_delegated else "No"
                worksheet.write(row_start + 3, col_idx, is_required)
                worksheet.write(row_start + 4, col_idx, field.field_description, label_header)

        if row_values and error_value:
            for count, line in enumerate(row_values, start=row_start + 1):
                if count in row_indices:
                    header = column_headers[count - row_start - 1]
                    if header in line:
                        line.remove(header)
                    for col_idx, data in enumerate(line, start=1):
                        worksheet.col(col_idx).width = col_width
                        worksheet.write(row_indices[count - row_start - 1], col_idx, data, label_header)

                elif count == row_start + len(column_headers):
                    worksheet.write(row_start + len(column_headers), len(line), "REASONS: (NOT CREATED RECORD)",
                                    label_header)
                    for each_error in error_value:
                        reason = set(each_error) & set(error_reason)
                        for col_idx, value in enumerate(each_error[1:], start=1):
                            worksheet.write(count, col_idx, str(value))
                        worksheet.write(count, len(each_error),
                                        f"{reason}: Value not found in Database! Please create it first.")

        workbook.save(fl)
        fl.seek(0)
        buf = base64.encodebytes(fl.read())
        ctx = dict(self._context, file=buf)
        self.env.args = self._cr, self._uid, misc.frozendict(ctx)
        file_id = self.env["wiz.template.file"].create({"file": buf, "name": f"{self.ir_model.model}.xls"})

        return {
            "res_id": file_id.id,
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wiz.template.file",
            "context": ctx,
            "target": "new",
        }

    def import_data(self):
        """This method is used for import data."""
        for rec in self:
            datafile = rec.upload_file
            file_name = str(rec.fname)

            # Checking for Suitable File
            if not datafile or not file_name.lower().endswith(".xls"):
                raise UserError(
                    _(
                        """Please select an (Downloded Blank Template)
                     .xls compatible file to Import"""
                    )
                )
            xls_data = base64.decodebytes(datafile)
            temp_path = tempfile.gettempdir()

            # writing a file to temp. location
            fp = open(temp_path + "/xsl_file.xls", "wb+")
            fp.write(xls_data)
            fp.close()

            # opening a file form temp. location
            wb = open_workbook(temp_path + "/xsl_file.xls")

            header_list = []
            data_list = []

            field_type_dict = {}
            headers_dict = {}
            flag_dict = {}

            row_values = []
            for sheet in wb.sheets():
                for rownum in range(sheet.nrows):
                    row_values.append(sheet.row_values(rownum))
                    # headers
                    if rownum == 12:
                        # (Checking condition based on Model/DocType: inside the template)
                        ir_model = [
                            x.strip().encode().decode("utf-8")
                            for x in sheet.row_values(rownum)
                        ]
                        model = self.ir_model.model
                        print("\n\n model", model)
                        ir_model_model = ir_model[1]
                        print("\n\n ir_model_model", ir_model_model)
                        # 10/0
                        if ir_model_model != model:
                            raise UserError(
                                _(
                                    """Selected document model not matched with browsed file!"""
                                )
                            )

                    if rownum == 13:
                        # converting unicode chars into string
                        header_key = [
                            x.strip().encode().decode("utf-8")
                            for x in sheet.row_values(rownum)
                        ]

                    elif rownum == 14:
                        # converting unicode chars into string
                        field_type_list = [
                            x.strip().encode().decode("utf-8").split(" Relation: ")
                            for x in sheet.row_values(rownum)
                        ]
                        list1 = []
                        list2 = []
                        for x in field_type_list:
                            list1.append(x[0])
                            if len(x) == 1:
                                list2.append(field_type_list.index(x))
                            else:
                                list2.append(x[1])
                        field_type_dict = dict(zip(header_key, zip(list1, list2)))

                    elif rownum == 15:
                        # converting unicode chars into string
                        flag_list = [
                            x.strip().encode().decode("utf-8")
                            for x in sheet.row_values(rownum)
                        ]
                        list1 = []
                        for x in flag_list:
                            list1.append(x)
                        if header_key and list1:
                            flag_dict = dict(zip(header_key, list1))

                        index = []
                        for x in header_list:
                            index.append(header_list.index(x))
                        if header_key and index:
                            headers_dict = dict(zip(header_key, index))

                    elif rownum == 16:
                        # converting unicode chars into string
                        header_list = [
                            x.strip().encode().decode("utf-8")
                            for x in sheet.row_values(rownum)
                        ]
                        index = []
                        for x in header_list:
                            index.append(header_list.index(x))
                        if header_key and index:
                            headers_dict = dict(zip(header_key, index))

                    # rows data
                    elif rownum >= 17:
                        data_list.append(sheet.row_values(rownum))

            # Data List
            if data_list and headers_dict:
                error_reason = []
                error_value = []
                for row in data_list:
                    vals = {}
                    for key in header_key:
                        if row[headers_dict[str(key)]]:
                            vals.update({str(key): row[headers_dict[str(key)]]})
                            if field_type_dict.get(str(key))[0] == "date":
                                try:
                                    date = datetime.strptime(
                                        row[headers_dict[str(key)]], "%Y/%m/%d"
                                    )
                                    vals.update({str(key): date})
                                except:
                                    raise UserError(
                                        _(
                                            """The Date format should
                                            be: YY/mm/dd << %s >>"""
                                        )
                                        % (row[headers_dict[str(key)]])
                                    )

                            elif field_type_dict.get(str(key))[0] == "datetime":
                                try:
                                    date = datetime.strptime(
                                        row[headers_dict[str(key)]], "%Y/%m/%d %H:%M:%S"
                                    )
                                    vals.update({str(key): date})
                                except:
                                    raise UserError(
                                        _(
                                            """The DateTime format should
                                            be: YY/mm/dd HH:MM:SS  << %s >> """
                                        )
                                        % (row[headers_dict[str(key)]])
                                    )

                            elif field_type_dict.get(str(key))[0] == "many2one":
                                search_id = (
                                    self.env[
                                        "" + str(field_type_dict.get(str(key))[1]) + ""
                                    ]
                                    .search(
                                        [("name", "=", row[headers_dict[str(key)]])],
                                        limit=1,
                                    )
                                    .id
                                )
                                self.create_m2o = True
                                if not search_id and self.create_m2o:
                                    ir_model_search = self.env["ir.model"].search(
                                        [
                                            (
                                                "model",
                                                "=",
                                                str(field_type_dict.get(str(key))[1]),
                                            )
                                        ]
                                    )
                                    required_field = [
                                        x.id
                                        for x in ir_model_search.field_id.filtered(
                                            lambda l: l.required
                                        )
                                    ]
                                    count = self.env["ir.model.fields"].search_count(
                                        [("id", "in", required_field)]
                                    )
                                    if count > 1:
                                        error_reason.append(row[headers_dict[str(key)]])
                                        error_value.append(row)
                                        vals.clear()
                                        break

                                    create_id = self.env[
                                        "" + str(field_type_dict.get(str(key))[1]) + ""
                                    ].create({"name": row[headers_dict[str(key)]]})
                                    vals.update({str(key): create_id and create_id.id})
                                    search_id = create_id.id
                                vals.update({str(key): search_id})

                            elif field_type_dict.get(str(key))[0] == "many2many":
                                ids = []
                                for line in row[headers_dict[str(key)]].split(";"):
                                    search_id = self.env[
                                        "" + str(field_type_dict.get(str(key))[1]) + ""
                                    ].search(
                                        [("name", "=", line)], limit=1, order="id desc"
                                    )
                                    self.create_m2m = True
                                    if not search_id and self.create_m2m:
                                        ir_model_search = self.env["ir.model"].search(
                                            [
                                                (
                                                    "model",
                                                    "=",
                                                    str(
                                                        field_type_dict.get(str(key))[1]
                                                    ),
                                                )
                                            ]
                                        )
                                        required_field = [
                                            x.id
                                            for x in ir_model_search.field_id.filtered(
                                                lambda l: l.required
                                            )
                                        ]
                                        count = self.env[
                                            "ir.model.fields"
                                        ].search_count([("id", "in", required_field)])
                                        if count > 1:
                                            error_reason.append(
                                                row[headers_dict[str(key)]]
                                            )
                                            error_value.append(row)
                                            vals.clear()
                                            break

                                        create_id = self.env[
                                            ""
                                            + str(field_type_dict.get(str(key))[1])
                                            + ""
                                        ].create({"name": line})
                                        ids.append(create_id and create_id.id)
                                        vals.update({str(key): [(6, 0, ids)]})
                                        search_id = self.env[
                                            ""
                                            + str(field_type_dict.get(str(key))[1])
                                            + ""
                                        ].search([("id", "=", create_id.id)])
                                    for search in search_id:
                                        ids.append(search and search.id)
                                        vals.update({str(key): [(6, 0, ids)]})

                            elif field_type_dict.get(str(key))[0] == "one2many":
                                vals.update({str(key): False})
                        else:
                            if (
                                flag_dict.get(str(key)) == "Yes"
                                and field_type_dict.get(str(key))[0] != "one2many"
                            ):
                                raise UserError(
                                    _("This field is required! << %s >>") % (str(key))
                                )
                            vals.update({str(key): False})
                        vals.pop("Column Name:", None)
                    for key in vals:
                        if not key:
                            del vals[key]
                            break
                    model_env = self.env["" + str(self.ir_model.model) + ""]
                    if vals != {}:
                        record_search_id = model_env.search(
                            [("name", "=", str(vals.get("name")))]
                        )
                        if record_search_id and self.update_only:
                            record_search_id.write(vals)
                        elif not record_search_id and self.create_only:
                            model_env.create(vals)

                if error_reason and error_value and row_values:
                    return self.download_template(row_values, error_reason, error_value)
        return {"context": {"close_previous_dialog": True}}


class WizTemplateFile(models.TransientModel):
    _name = "wiz.template.file"
    _description = "Wiz Template File"

    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}
        ctx = self._context
        res = super(WizTemplateFile, self).default_get(fields)
        if self._context.get("file"):
            res.update({"file": ctx["file"]})
        return res

    file = fields.Binary("File")
    name = fields.Char(string="File Name", size=32)
