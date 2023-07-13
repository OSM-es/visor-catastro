import sys

import click
import geopandas as gpd
import gzip
import osm2geojson


dist_path = '/data/dist/'
update_path = '/data/update/'


class Diff():
    "Compares two osm datasets"
    def __init__(self, mun_code1, task1, data1, mun_code2, task2, data2):
        columns = ['mun_code', 'task', 'tags', 'geometry']
        self.df1 = gpd.GeoDataFrame(columns=columns)
        self.df2 = gpd.GeoDataFrame(columns=columns)
        Diff.shapes_to_dataframe(self.df1, data1, mun_code1, task1)
        Diff.shapes_to_dataframe(self.df2, data2, mun_code2, task2)
        self.fixmes = []

    @staticmethod
    def get_shapes(fn):
        """Read osm.gz file to geojson shapes"""
        with gzip.open(fn) as fo:
            xml = fo.read()
        return osm2geojson.xml2shapes(xml)

    @staticmethod
    def shapes_to_dataframe(df, data, mun_code, task):
        """Convert geojson to dataframe"""
        for feat in data:
            geom = feat['shape']
            tags = feat['properties']['tags']
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
            # TODO: si g es un nodo, habrá que hacer un buffer y filtrar candidatos por tipo
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

    def add_fixme(self, feat, text):
        fixme = {
            'geom': feat.geometry.point_on_surface(),
            'mun_code': feat.mun_code,
            'task': feat.task,
            'fixme': text,
        }
        self.fixmes.append(fixme)

    def update_matches(self, matches):
        for i1, i2 in matches:
            fixme = None
            feat = None
            if i1 is None:
                feat = self.df2.loc[i2]
                fixme = 'Creado o agregado'
            elif i2 is None:
                feat = self.df1.loc[i1]
                fixme = 'Eliminado o segregado'
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
                msg = fixme + ' ' + feat.geometry.geom_type
                if feat.tags: msg += str(feat.tags)
                self.add_fixme(feat, msg)


    def run(self):
        matches = Diff.get_matches(self.df1, self.df2)
        self.update_matches(matches)


@click.command()
@click.argument('old')
@click.argument('new')
def command(old, new):
    mun_code1, task1 = old.split('-')
    mun_code2, task2 = new.split('-')
    fn1 = dist_path + mun_code1 + '/tasks/' + task1 + '.osm.gz'
    fn2 = update_path + mun_code2 + '/tasks/' + task2 + '.osm.gz'
    data1 = Diff.get_shapes(fn1)
    data2 = Diff.get_shapes(fn2)

    diff = Diff(mun_code1, task1, data1, mun_code2, task2, data2)
    diff.run()
    for f in diff.fixmes:
        print(f['task'], f['fixme'])

if __name__ == '__main__':
    command()
