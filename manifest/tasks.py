from firebase import FirebaseApplication, FirebaseAuthentication
#from firebase import Firebase
import firebase
from celery.decorators import task
from ansible import utils
import ansible.runner, json, os


@task()
def ansible_jeneric(job_id, user_id):

    # firebase authentication
    SECRET = os.environ['SECRET']
    authentication = FirebaseAuthentication(SECRET, True, True)

    # set the specific job from firebase with user
    user = 'simplelogin:' + user_id
    URL = 'https://deploynebula.firebaseio.com/users/' + user + '/external_data/'
    myExternalData = FirebaseApplication(URL, authentication)

    # update status to RUNNING in firebase
    myExternalData.patch(job_id, json.loads('{"status":"RUNNING"}'))

    # finally, get the actual job
    job = myExternalData.get(URL, job_id)

    myHostList = job['host_list'] +','
    myModuleName = job['module_name']
    myModuleArgs = job['module_args']
    myPattern = job['pattern']
    myRemoteUser = job['remote_user']
    myRemotePass = job['remote_pass']

    runString = ""

    for arg in myHostList, myModuleName, myModuleArgs, myPattern, myRemoteUser, myRemotePass:
        if ( arg ):
            runString = runString + arg

    results = ansible.runner.Runner(
        pattern=myPattern,
        forks=10,
        module_name=myModuleName,
        module_args=myModuleArgs,
        remote_user=myRemoteUser,
        remote_pass=myRemotePass,
        host_list=myHostList,
    ).run()
    # run the ansible stuffs
    #results = ansible.runner.Runner(
    #    pattern=myHost, forks=10,
    #    module_name='command', module_args=myCommand,
    #).run()

    # get it to a good format
    #data = json.loads(results)
    #data = json.dumps(results)

    # set status to COMPLETE
    myExternalData.patch(job_id, json.loads('{"status":"COMPLETE"}'))

    if type(results) == dict:
        results = utils.jsonify(results)

    # post results to firebase
    myExternalData.post(job_id + '/returns', results)
    #returns.patch(job_id + '/returns', json.dumps(results))
    return results
