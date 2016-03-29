"""Ajax views for tower metadata app."""
from . import ajax
from tasks import create_metadata_task
from flask import jsonify, request, url_for


@ajax.route('/status/<task_id>')
def taskstatus(task_id):
    """Get the task status for <task_id>."""
    task = create_metadata_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'status': 'Pending...',
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'url': task.info.get('url', 0)
            # 'current': task.info.get('current', 0),
            # 'total': task.info.get('total', 1),
            # 'status': task.info.get('status', '')
        }
        # if 'result' in task.info:
        #    response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@ajax.route('/create_metadata', methods=['POST'])
# @login_required
def create_metadata():
    """Inititate metadata generation."""
    year = request.form["year"]
    doy = request.form["doy"]
    task = create_metadata_task.delay(year=year, doy=doy)
    return jsonify({}), 202, {'Location': url_for('.taskstatus',
                                                  task_id=task.id)}
