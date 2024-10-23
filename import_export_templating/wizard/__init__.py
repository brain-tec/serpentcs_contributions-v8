# See LICENSE file for full copyright and licensing details.

from . import wiz_download_template

def download_template(self, row_values=None, error_reason=None, error_value=None):
    """This method is used for export template."""
    fl = BytesIO()
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(self.ir_model.name)

    # Define Styles
    bold = xlwt.easyxf("font: bold 1;")
    main_header = xlwt.easyxf(
        "font: bold 1, height 270;"
        " align: horiz center,vert center ,wrap 1;"
        "borders :top hair, bottom hair,left hair, right hair, "
        "bottom_color black,top_color black"
    )
    label_header = xlwt.easyxf(
        "font: bold 1, height 230;"
        " align: horiz center,vert center ,wrap 1;"
        "borders :top hair, bottom hair,left hair, right hair, "
        "bottom_color black,top_color black"
    )

    self._setup_worksheet_layout(worksheet, main_header, bold)

    if not self.fields_list_ids and not error_value:
        raise UserError(_("Fields should not be blank!"))

    if self.fields_list_ids:
        self._populate_field_data(worksheet, label_header)
    elif row_values and error_value:
        self._populate_error_data(worksheet, row_values, error_reason, error_value, label_header)

    workbook.save(fl)
    fl.seek(0)
    buf = base64.encodebytes(fl.read())
    ctx = dict(self._context)
    vals = {"file": buf}
    ctx.update(vals)
    self.env.args = self._cr, self._uid, misc.frozendict(ctx)
    file_id = self.env["wiz.template.file"].create(
        {"file": buf, "name": self.ir_model.model + ".xls"}
    )
    print("\n\n\n self.ir_model.model", self.ir_model.model)

    return {
        "res_id": file_id.id,
        "type": "ir.actions.act_window",
        "view_type": "form",
        "view_mode": "form",
        "res_model": "wiz.template.file",
        "context": ctx,
        "target": "new",
    }

def _setup_worksheet_layout(self, worksheet, main_header, bold):
    """Configure the initial layout of the worksheet."""
    worksheet.row(0).height = 500
    for i, width in enumerate([6200, 9500, 9500, 9500, 9500]):
        worksheet.col(i).width = width

    worksheet.write_merge(0, 0, 0, 4, "Data Import Template", main_header)
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

    data_import_notes = [
        'Many2one: You can enter "NAME" of the relational model!',
        'Many2many: You can enter "Name" of the relational model, separate by ";"',
        "One2many: Let this blank! & Download Blank Template for displayed comodel to Import!",
        "There should only be one required field in relational model for creation of new record.",
    ]
    worksheet.write_merge(3, 3, 3, 4, "Data Import Notes:", bold)
    for idx, note in enumerate(data_import_notes, start=5):
        worksheet.write_merge(idx, idx, 3, 4, note)

    headers = ["DocType:", "DocType", "Type:", "Mandatory:", "Column Labels:", "Start entering data this line"]

    default_style = xlwt.easyxf("font: height 200;")

    for row, header in enumerate(headers, start=12):
        style_to_use = bold if row != 16 else default_style
        worksheet.write(row, 0, header, style_to_use)

def _populate_field_data(self, worksheet, label_header):
    """Populate field-related data in the worksheet."""
    for col_index, line in enumerate(self.fields_list_ids, start=1):
        worksheet.col(col_index + 1).width = 9900
        worksheet.write(13, col_index, line.name)
        field_info = f"{line.ttype} Relation: {line.relation}"
        worksheet.write(14, col_index, field_info)

        is_delegated = (
                (line.ttype == "many2one" and line.relation in [x.model for x in
                                                                self.ir_model.inherited_model_ids] and not line.related)
                or line.ttype == "one2many"
        )
        is_required = "Yes" if line.required and not is_delegated else "No"
        worksheet.write(15, col_index, is_required)
        worksheet.write(16, col_index, line.field_description, label_header)

def _populate_error_data(self, worksheet, row_values, error_reason, error_value, label_header):
    """Populate error-related data in the worksheet."""
    column_headers = ["Column Name:", "Type:", "Mandatory:", "Column Labels:"]
    row_indices = [13, 14, 15, 16]

    for row_idx, line in enumerate(row_values):
        if row_idx in (0, 1, 2, 3):
            header = column_headers[row_idx]
            if header in line:
                i = line.index(header)
                del line[i]
                for col, data in enumerate(line, start=1):
                    worksheet.col(col).width = 9900
                    worksheet.write(row_indices[row_idx], col, data, label_header if row_idx == 3 else None)

        if row_idx == 4:
            worksheet.write(16, len(line), "REASONS: (NOT CREATED RECORD)", label_header)

    row_start = 17
    for each_error in error_value:
        del each_error[0]
        reason = set(each_error) & set(error_reason)
        for col, value in enumerate(each_error, start=1):
            worksheet.col(col).width = 9900
            worksheet.write(row_start, col, str(value))
        worksheet.write(row_start, len(each_error) + 1,
                        f"{str(reason)}: Value not found in Database! Please create it first. Once created, remove (REASON) column for IMPORT!")
        row_start += 1
