from web_app import app

with app.test_client() as c:
    # 1) POST to index to set session
    r = c.post('/', data={'name':'TestUser', 'mobile':'9999999999'}, follow_redirects=True)
    print('Index POST ->', r.status_code)

    # 2) POST to search
    r = c.post('/search', data={'from':'madurai', 'to':'coimbatore', 'date':'2026-01-10'}, follow_redirects=True)
    print('Search POST ->', r.status_code, 'URL:', r.request.path)

    # 3) GET seats page
    r = c.get('/seats?from=madurai&to=coimbatore&date=2026-01-10')
    print('Seats GET ->', r.status_code)

    # 4) POST to payment
    r = c.post('/payment', data={
        'seat': 'S1',
        'count': '1',
        'date': '2026-01-10',
        'from_place': 'madurai',
        'to_place': 'coimbatore'
    }, follow_redirects=True)

    print('Payment POST ->', r.status_code)
    text = r.get_data(as_text=True)
    if r.status_code == 200 and 'Payment Page' in text:
        print('SUCCESS: Landed on Payment page')
    else:
        print('FAILED: Response snippet:\n', text[:500])
