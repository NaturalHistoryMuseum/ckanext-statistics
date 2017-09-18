import ckan.plugins as p


def view_stats(context, data_dict):

    authorized = p.toolkit.check_access('view_stats', context, data_dict)

    if not authorized:
        return {
            'success': False,
            'msg': p.toolkit._('User not authorized to view stats')
        }
    else:
        return {'success': True}
