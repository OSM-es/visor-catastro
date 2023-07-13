import sys

import click
import geopandas as gpd
import gzip
import osm2geojson


dist_path = '/data/dist/'
update_path = '/data/update/'


class Diff():
    "Class to compare two osm datasets"
    def __init__(self, df1, df2):
        self.df1 = df1
        self.df2 = df2
        self.fixmes = []
        self.demolished = []

    @staticmethod
    def parse_args(source_path, args):
        """Read command args to geojson shapes.
        args is a list of <mun_code>-<taskfilename>
        """
        for mun_code, task in [arg.split('-') for arg in args]:
            fn = source_path + mun_code + '/tasks/' + task + '.osm.gz'
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
        return gpd.GeoDataFrame(columns=['mun_code', 'task', 'tags', 'geometry'])

    @staticmethod
    def shapes_to_dataframe(df, data, mun_code, task):
        """Convert geojson to dataframe"""
        for feat in data:
            geom = feat['shape']
            tags = feat['properties'].get('tags')
            if tags:
                df.loc[len(df)] = [mun_code, task, tags, geom]

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

    @staticmethod
    def get_matches(df1, df2):
        """
        Return [
            (
                matching index in df1 or none (new),
                matching index in df2 or none (deleted),
            )
        ]
        """
        nx = df1.geometry.sindex
        matches = []
        matches1 = []
        for i in df2.index:
            g = df2.geometry[i]
            candidates = nx.query(g, predicate="intersects")
            match = Diff.get_match(g, [df1.iloc[c].geometry for c in candidates])
            if match is not None:
                i1 = df1.index[candidates[match]]
                matches.append((i1, i))
                matches1.append(i1)
            else:
                matches.append((None, i))
        for i in df1.index:
            if i not in matches1:
                matches.append((i, None))
        return matches

    def get_fixme(self, feat, text):
        msg = text + ' ' + feat.geometry.geom_type
        tags = {k: v for k, v in feat.tags.items() if k not in ('fixme', 'ref', 'addr:cat_name')}
        msg += str(tags)
        return {
            'geom': feat.geometry,
            'node': feat.geometry.point_on_surface(),
            'mun_code': feat.mun_code,
            'task': feat.task,
            'fixme': msg,
        }

    def update_matches(self, matches):
        for i1, i2 in matches:
            fixme = None
            feat = None
            demolished = False
            if i1 is None:
                feat = self.df2.loc[i2]
                fixme = 'Creado' if feat.geometry.geom_type == 'Point' else 'Creado o agregado'
            elif i2 is None:
                feat = self.df1.loc[i1]
                fixme = 'Eliminado' if feat.geometry.geom_type == 'Point' else 'Eliminado o segregado'
                demolished = True
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
                if demolished:
                    self.demolished.append(self.get_fixme(feat, fixme))
                else:
                    self.fixmes.append(self.get_fixme(feat, fixme))


    def run(self):
        matches = Diff.get_matches(self.df1, self.df2)
        self.update_matches(matches)


@click.command()
@click.argument('old', nargs=-1)
@click.option('--new', '-n', multiple=True)
def command(old, new):
    df1 = Diff.parse_args(dist_path, old)
    df2 = Diff.parse_args(update_path, new)
    diff = Diff(df1, df2)
    diff.run()
    for f in diff.fixmes:
        print(f['task'], f['fixme'])
    print('----------------------')
    for f in diff.demolished:
        print(f['task'], f['fixme'])


if __name__ == '__main__':
    command()
