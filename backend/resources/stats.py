from flask_restful import Resource

import models


class Stats(Resource):
    def get(self, code=None):
        return {
            'buildings': models.Task.count_buildings(code),
            'addresses': models.Task.count_addresses(code),
            'users': models.User.query.count(),
            'mappers': models.Task.count_mappers(code),
        }


class TasksStatus(Resource):
    def get(self, code=None):
        labels = [s.name for s in models.Task.Status]
        labels.append('LOCKED-' + models.TaskLock.Action.MAPPING.name)
        labels.append('LOCKED-' + models.TaskLock.Action.VALIDATION.name)
        bu_stats = models.Task.status_stats(code, 'bu_status')
        bu_map_locks = models.Task.count_locks(code, models.TaskLock.Action.MAPPING, 'buildings')
        bu_val_locks = models.Task.count_locks(code, models.TaskLock.Action.VALIDATION, 'buildings')
        bu_stats.append(bu_map_locks)
        bu_stats.append(bu_val_locks)
        ad_stats = models.Task.status_stats(code, 'ad_status')
        ad_map_locks = models.Task.count_locks(code, models.TaskLock.Action.MAPPING, 'addresses')
        ad_val_locks = models.Task.count_locks(code, models.TaskLock.Action.VALIDATION, 'addresses')
        ad_stats.append(ad_map_locks)
        ad_stats.append(ad_val_locks)
        return {
            'buildings': dict(zip(labels, bu_stats)),
            'addresses': dict(zip(labels, ad_stats)),
            'splitted': bu_stats != ad_stats
        }


class ContributorStats(Resource):
    def get(self, code):
        contributors = models.TaskHistory.get_contributors(code)
        return {
            'mappers': models.TaskHistory.count_mappers(code),
            'validators': models.TaskHistory.count_validators(code),
            'contributors': [u.import_user.asdict() for u in contributors],
        }

class TimeStats(Resource):
    def get(self, code):
        total_tasks = models.Task.query_by_code(code).count()
        mtime, mtasks = models.TaskHistory.get_time(
            code, models.TaskHistory.Action['LOCKED_FOR_MAPPING']
        )
        average_mapping_time = 0
        if mtasks > 0: average_mapping_time = mtime / mtasks
        vtime, vtasks = models.TaskHistory.get_time(
            code, models.TaskHistory.Action['LOCKED_FOR_VALIDATION']
        )
        average_validation_time = 0
        if vtasks > 0: average_validation_time = vtime / vtasks

        time_to_finish_mapping = (total_tasks - mtasks) * average_mapping_time
        time_to_finish_validation = (total_tasks - vtasks) * average_validation_time

        return {
            'total_tasks': total_tasks,
            'tasks_to_map': total_tasks - mtasks,
            'tasks_to_validate': total_tasks - vtasks,
            'average_mapping_time': average_mapping_time,
            'average_validation_time': average_validation_time,
            'time_to_finish_mapping': time_to_finish_mapping,
            'time_to_finish_validation': time_to_finish_validation,
        }