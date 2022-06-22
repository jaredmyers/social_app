import json
from log_publisher import send_log


def accessor_methods(body, queue):
    '''
    Simulated driver for api queries
    '''
    def get_details(body):
        '''returns simulated api results'''
        results = {
                "tracks": ["As It Was", "Light Switch", "Oh My God"],
                "artists": ["Harry Styles", "Charlie Puth", "Shawn Mendes"],
                "genres": ["Metal", "Pop", "Trap"],
                "albums": ["It'll Be Okay", "Sunflower"],
                "preview": []
                    }

        #send_log('got match details, returning..\n')
        return json.dumps(results)

    # main entry point
    print('body of api_accessor_methods:')
    body = body.decode('utf-8')
    body = json.loads(body)
    print(body)

    if body['type'] == 'get_details':
        return get_details(body)
    else:
        print('api_accessor_meth detected no valid body value')
