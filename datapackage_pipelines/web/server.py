import datetime

from flask import Flask, render_template, abort, redirect
import yaml
import slugify

from ..manager.status import status

app = Flask(__name__)


def datestr(x):
    return str(datetime.datetime.fromtimestamp(x))


def yamlize(x):
    ret = yaml.dump(x, default_flow_style=False)
    return ret


@app.route("/")
def main():
    statuses = sorted(status.all_statuses(), key=lambda x: x.get('id'))
    for pipeline in statuses:
        for key in ['ended', 'last_success', 'started']:
            if pipeline.get(key):
                pipeline[key] = datestr(pipeline[key])
        pipeline['class'] = {'INIT': 'primary',
                             'REGISTERED': 'primary',
                             'INVALID': 'danger',
                             'RUNNING': 'warning',
                             'SUCCEEDED': 'success',
                             'FAILED': 'danger'
                            }[pipeline.get('state', 'INIT')]

        pipeline['slug'] = slugify.slugify(pipeline['id'])
        print(pipeline.keys())
    return render_template('dashboard.html',
                           pipelines=statuses,
                           yamlize=yamlize)


@app.route("/badge/<path:pipeline_id>")
def badge(pipeline_id):
    if not pipeline_id.startswith('./'):
        pipeline_id = './' + pipeline_id
    pipeline_status = status.get_status(pipeline_id)
    if pipeline_status is None:
        abort(404)
    status_text = pipeline_status.get('message')
    success = pipeline_status.get('success')
    if success is True:
        record_count = pipeline_status.get('record_count')
        if record_count is not None:
            status_text += ' (%d records)' % record_count
        status_color = 'brightgreen'
    elif success is False:
        status_color = 'red'
    else:
        status_color = 'lightgray'
    return redirect('https://img.shields.io/badge/{}-{}-{}.svg'.format(
        'pipeline', status_text, status_color
    ))
