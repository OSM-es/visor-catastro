from sqlalchemy import and_
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
          'labels': labels,
          'buildings': bu_stats,
          'addresses': ad_stats,
      }
