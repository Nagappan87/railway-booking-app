from web_app import app
import os

with app.test_client() as c:
    c.post('/', data={'name':'Ratheesh', 'mobile':'9999999999'})
    print('os.path.exists static/ratheesh gpay.jpeg ->', os.path.exists(os.path.join('static','ratheesh gpay.jpeg')))
    r = c.post('/search', data={'from':'madurai', 'to':'coimbatore', 'date':'2026-01-10'}, follow_redirects=True)
    r = c.post('/payment', data={
        'seat': 'S1',
        'count': '1',
        'date': '2026-01-10',
        'from_place': 'madurai',
        'to_place': 'coimbatore'
    }, follow_redirects=True)

    text = r.get_data(as_text=True)
    found = 'ratheesh gpay.jpeg' in text
    print('Payment page includes owner QR:', found)
    print('Contains <img src="/static":', '<img src="/static' in text)
    if not found:
        print(text)
