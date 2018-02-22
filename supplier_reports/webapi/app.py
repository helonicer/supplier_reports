from flask import ( Flask, request, redirect, url_for,flash ,request, send_from_directory)
from werkzeug.utils import secure_filename
import os
from supplier_reports import conf as g
from supplier_reports.gen_reports import gen_reports
import flask


app = Flask("webapi", static_url_path='')

class HtmlPage(object):
    template = """<!doctype html>
    <html>
      <head>
        {head}
        <title>My Page</title>
      </head>
      <body>
        <div id="content">{body}</div>
      </body>
    </html>
    """

    def __init__(self, msgs=None, headers=None):
        self.body=[]
        self.head=[]
        if msgs:
            if isinstance(msgs, list):
                self.body.extend(msgs)
            else:
                self.body.append(msgs)
        if headers:
            self.head.extend(headers)

    def render(self):
        return HtmlPage.template.format(body="".join(self.body), head="".join(self.head))

    def add_body(self, body):
        self.body.append(body)

    def add_head(self, header):
        self.head.append(header)


def render_html_page(msgs, headers=None):
    return HtmlPage(msgs, headers=headers).render()


def csv_to_html_table(file_path, headers=None, delimiter=","):
    with open(file_path) as f:
        content = f.readlines()
    #reading file content into list
    rows = [x.strip() for x in content]
    table = "<table border=1>"
    #creating HTML header row if header is provided
    if headers is not None:
        table+= "\n".join(["\n\t<th>"+cell+"</th>" for cell in headers.split(delimiter)])
    else:
        table+= "\n".join(["\n\t<th>"+cell+"</th>" for cell in rows[0].split(delimiter)])
        rows=rows[1:]
    #Converting csv to html row by row
    for row in rows:
        table+= "\n\t<tr>" + "".join(["\n\t\t<td>"+cell+"</td>" for cell in row.split(delimiter)]) + "</tr>" + "\n"
    table+="</table><br>"
    return table


def csv_to_html_file(file_path):
    html_table=csv_to_html_table(file_path)
    html_page = render_html_page(msgs=html_table)
    with open(file_path + ".html","wt") as fp:
        fp.write(html_page)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            if not file.filename.endswith("xlsx"):
                flask.abort(400, "not excel file '{}".format(file.filename))
            uploadfilename = secure_filename(file.filename)
            file_path = os.path.join(g.config.root.reports_dir, uploadfilename)
            file.save(file_path)
            csv_reports = gen_reports(file_path)
            msgs = ["<h3>generated reports</h3><br>"]
            for report in csv_reports:
                if report is not None:
                    report_file_name=report.get_report_file_name()
                    report.save(g.config.root.reports_dir)
                    csv_to_html_file(os.path.join(g.config.root.reports_dir,report.get_report_file_name()))
                    msgs.append('{}: '
                                '<a href="/reports/{}.html">view</a>, '
                                '<a href="/reports/{}">download</a><br>'.format(report_file_name, report_file_name, report_file_name))


            return render_html_page(msgs)
            #return redirect(url_for('ack_upload',filename=filename))



    return '''
    <!doctype html>
    <html>
    <head>
    </head>
    <body>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <!--
    <h2>Examples of working reports</h2>
    <ol>
        <li><a href="/reports/orders_export_02_14_2018_up.xlsx">orders_export_02_14_2018_up.xlsx</a></li>
        <li><a href="/reports/orders_export_test.xlsx">orders_export_test.xlsx</a></li>
    </ol>-->
    </body>
    </html>
    '''

@app.route('/ack_uploaded')
def ack():
    filename = request.args.get("filename", default=None)
    msg = "uploaded {}".format(filename)
    headers = ['<meta http-equiv="refresh" content="5;URL=/" />']
    return render_html_page(msg, headers)


@app.route('/reports/<path:path>')
def send_reports(path):
    return send_from_directory(g.config.root.reports_dir, path)


def main():
    app.run(host='0.0.0.0', port=8999, debug=True)


if __name__=='__main__':
    main()

