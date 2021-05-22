from sqlalchemy import or_


def get_default(parameters, metadata, obj):
    if ('orderBy' or 'orderType') not in parameters:
        order = obj.id.asc()
    else:
        try:
            if parameters['orderType'] == 'desc':
                order = metadata[parameters['orderBy']].desc()
            else:
                order = metadata[parameters['orderBy']].asc()
        except:
            order = obj.id.asc()
    if 'limit' not in parameters:
        limit = 20
    else:
        try:
            limit = int(parameters['limit'])
        except:
            limit = 20
    if 'page' not in parameters:
        page = 1
    else:
        try:
            page = int(parameters['page'])
        except:
            page = 1
    offset = (page - 1) * limit

    return limit, page, offset, order


def standardized_data(obj, del_param=None, param=None):
    data = {}
    try:
        obj = obj.__dict__
    except:
        return None
    try:
        if '_sa_instance_state' in obj:
            del obj["_sa_instance_state"]
    except:
        pass
    if del_param is not None:
        for d in del_param:
            try:
                del obj[d]
            except:
                pass
    if param is not None:
        for p in param:
            data[p] = obj[param[p]]
        return data

    return obj


def process_data(data, session_tmp, obj, is_brand):
    if is_brand:
        return standardized_data(data)
    data = standardized_data(data)
    data['images'] = data['images'].split(',')
    data['brand'] = session_tmp.query(obj).filter_by(id=data['brand_id']).first().brand
    return data


def get_data_with_page(data, page_limit, current_page, total):
    result = {'data': data, 'paging': {'total_count': total}}

    if int(result['paging']['total_count']) % int(page_limit) == 0:
        total_page = int(result['paging']['total_count']) // int(page_limit)
    else:
        total_page = (int(result['paging']['total_count']) // int(page_limit)) + 1

    if current_page < int(total_page):
        result['paging']['records_in_page'] = page_limit
    else:
        result['paging']['records_in_page'] = int(result['paging']['total_count']) - (
                int(current_page) - 1) * page_limit

    result['paging']['total_page'] = total_page
    result['paging']['current_page'] = int(current_page)

    return result


def check_search(query, parameters, obj):
    if "search" in parameters and parameters['search'] != "":
        search_values = parameters['search'].split(",")
        for search_value in search_values:
            query = query.filter(or_(key.like('%' + search_value + '%') for key in obj.__table__.columns))
    return query


def get_brands(session, brand_obj):
    brands = session.query(brand_obj)
    brands = brands.all()

    camera_brands = []
    laptop_brands = []

    for i in range(len(brands)):
        brands[i] = process_data(brands[i], None, None, True)
        if brands[i]['is_laptop']:
            laptop_brands.append(brands[i])
        else:
            camera_brands.append(brands[i])
    return camera_brands, laptop_brands


def get_products(session, parameters, product_obj, brand_obj, order, offset, limit, brand_id=False):
    if not brand_id:
        products = session.query(product_obj)
    else:
        products = session.query(product_obj).filter_by(brand_id=brand_id)
    products = check_search(products, parameters, product_obj)
    total_count = products.count()
    products = products.order_by(order).offset(offset).limit(limit).all()

    for i in range(len(products)):
        products[i] = process_data(products[i], session, brand_obj, False)
    return products, total_count
