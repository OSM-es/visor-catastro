import sys

import click
import geopandas as gpd
import gzip
import osm2geojson

from config import Config

UPDATE = Config.UPDATE_PATH
DIST = Config.DIST_PATH


class Diff():
    "Class to compare two osm datasets"
    def __init__(self, df1=None, df2=None, demolished=[]):
        self.df1 = Diff.dataframe() if df1 is None else df1
        self.df2 = Diff.dataframe() if df2 is None else df2
        self.fixmes = []
        self.demolished = demolished

    @staticmethod
    def get_filename(source_path, mun_code, task):
        return source_path + mun_code + '/tasks/' + task + '.osm.gz'

    @staticmethod
    def parse_args(source_path, args):
        """Read command args to geojson shapes.
        args is a list of <mun_code>-<taskfilename>
        """
        for mun_code, task in [arg.split('-') for arg in args]:
            fn = Diff.get_filename(source_path, mun_code, task)
            data = Diff.get_shapes(fn)
            df = Diff.dataframe()
            Diff.shapes_to_dataframe(df, data, mun_code, task)
        return df

    @staticmethod
    def get_shapes(fn):
        """Read osm.gz file to geojson shapes"""
        with gzip.open(fn) as fo:
            xml = fo.read()
        return osm2geojson.xml2shapes(xml, filter_used_refs=False)

    @staticmethod
    def dataframe():
        columns = ['mun_code', 'task', 'task_id', 'tags', 'geometry']
        return gpd.GeoDataFrame(columns=columns)

    @staticmethod
    def shapes_to_dataframe(df, data, mun_code, task, task_id=None):
        """Convert geojson to dataframe"""
        for feat in data:
            Diff.add_row(df, mun_code, task, task_id, feat)

    @staticmethod
    def add_row(df, mun_code, task, task_id, feature):
        geom = feature['shape']
        tags = feature['properties'].get('tags')
        if tags:
            df.loc[len(df)] = [mun_code, task, task_id, tags, geom]

    @staticmethod
    def get_match(geom, candidates):
        """
        Returns the index of the geometry in the candidates list that most 
        closely resembles geom or None
        """
        match = None
        match_area = 0
        for i, c in enumerate(candidates):
            intersected_area = c.intersection(geom).area
            if c.area != 0 and intersected_area > match_area:
                match = i
                match_area = intersected_area
        return match

    def _update_matches(self, matches):
        for i1, i2 in matches:
            fixme = None
            feat = None
            if i1 is None:
                feat = self.df2.loc[i2]
                feat1 = feat
                fixme = 'Creado' if feat.geometry.geom_type == 'Point' else 'Creado o agregado'
            elif i2 is None:
                feat = self.df1.loc[i1]
                fixme = 'Eliminado' if feat.geometry.geom_type == 'Point' else 'Eliminado o segregado'
            else:
                feat1 = self.df1.loc[i1]
                feat = self.df2.loc[i2]
                geom_diff = not feat.geometry.simplify(0.000000001).equals(
                    feat1.geometry.simplify(0.000000001)
                )
                tags_diff = feat.tags != feat1.tags
                if geom_diff:
                    if tags_diff:
                        fixme = "Varia la geometría y las etiquetas de"
                    else:
                        fixme = "Varia la geometría de"
                elif tags_diff:
                    fixme = "Varia las etiquetas de"
            if fixme:
                if i2 is None:
                    self.demolished.append(self.new_fixme(feat, feat, fixme))
                else:
                    self.fixmes.append(self.new_fixme(feat, feat1, fixme))

    def get_fixmes(self):
        """
        Return [
            (
                matching index in df1 or none (new),
                matching index in df2 or none (deleted),
            )
        ]
        """
        nx = gpd.GeoSeries(self.df1.geometry).sindex
        matches = []
        matches1 = []
        for i in self.df2.index:
            g = self.df2.geometry[i]
            candidates = nx.query(g, predicate="intersects")
            match = Diff.get_match(g, [self.df1.loc[c].geometry for c in candidates])
            if match is not None:
                i1 = self.df1.index[candidates[match]]
                matches.append((i1, i))
                matches1.append(i1)
            else:
                matches.append((None, i))
        for i in self.df1.index:
            if i not in matches1:
                matches.append((i, None))
        self._update_matches(matches)

    def clean_demolished(self, geom):
        for i in range(len(self.demolished) - 1, -1, -1):
            if self.demolished[i]['geom'] == geom:
                self.demolished.remove(self.demolished[i])

    def new_fixme(self, new_feat, old_feat, text):
        msg = text + ' ' + new_feat.geometry.geom_type
        tags = {k: v for k, v in new_feat.tags.items() if k not in ('fixme', 'ref', 'addr:cat_name')}
        msg += str(tags)
        return {
            'geom': new_feat.geometry,
            'node': new_feat.geometry.point_on_surface(),
            'mun_code': None if old_feat is None else old_feat.mun_code,
            'task': None if old_feat is None else old_feat.task,
            'fixme': msg,
        }
    


@click.command()
@click.argument('old', nargs=-1)
@click.option('--new', '-n', multiple=True)
def command(old, new):
    df1 = Diff.parse_args(DIST, old)
    df2 = Diff.parse_args(UPDATE, new)
    diff = Diff(df1, df2)
    diff.get_fixmes()
    for f in diff.fixmes:
        print(f['task'], f['fixme'])
    print('----------------------')
    for f in diff.demolished:
        print(f['task'], f['fixme'])


if __name__ == '__main__':
    command()
