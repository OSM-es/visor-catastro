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
    def __init__(self, df1=None, df2=None):
        self.df1 = Diff.dataframe() if df1 is None else df1
        self.df2 = Diff.dataframe() if df2 is None else df2
        self.fixmes = []

    @staticmethod
    def get_filename(source_path, mun_code, localid):
        return source_path + mun_code + '/tasks/' + localid + '.osm.gz'

    @staticmethod
    def parse_args(source_path, args):
        """Read command args to geojson shapes.
        args is a list of <mun_code>-<taskfilename>
        """
        for mun_code, localid in [arg.split('-') for arg in args]:
            fn = Diff.get_filename(source_path, mun_code, localid)
            data = Diff.get_shapes(fn)
            df = Diff.dataframe()
            Diff.shapes_to_dataframe(df, data)
        return df

    @staticmethod
    def get_shapes(fn):
        """Read osm.gz file to geojson shapes"""
        with gzip.open(fn) as fo:
            xml = fo.read()
        return osm2geojson.xml2shapes(xml, filter_used_refs=False)

    @staticmethod
    def dataframe():
        return gpd.GeoDataFrame(columns=['tags', 'geometry'])

    @staticmethod
    def shapes_to_dataframe(df, data):
        """Convert geojson to dataframe"""
        for feat in data:
            Diff.add_row(df, feat)

    @staticmethod
    def add_row(df, feature):
        geom = feature['shape']
        tags = feature['properties'].get('tags')
        if tags:
            df.loc[len(df)] = [tags, geom]

    @staticmethod
    def clean_tags(tags):
        private_tags = ('fixme', 'ref', 'addr:cat_name')
        tags = {k: v for k, v in tags.items() if k not in private_tags}
        return tags
        
    @staticmethod
    def get_match(geom, candidates):
        """
        Returns the index of the geometry in the candidates list that most 
        closely resembles geom or None
        """
        match = None
        match_factor = 9E9
        for i, c in enumerate(candidates):
            if geom.geom_type == 'Point' and c.geom_type == 'Point':
                f = geom.distance(c)
            else:
                f = max(geom.area, c.area) - c.intersection(geom).area
            if f < match_factor:
                match = i
                match_factor = f
        return match

    def _update_matches(self, matches):
        for i1, i2 in matches:
            fixme = None
            feat = None
            if i1 is None:
                feat = self.df2.loc[i2]
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
                tags_diff = Diff.clean_tags(feat.tags) != Diff.clean_tags(feat1.tags)
                if geom_diff:
                    if tags_diff:
                        fixme = "Varia la geometría y las etiquetas de"
                    else:
                        fixme = "Varia la geometría de"
                elif tags_diff:
                    fixme = "Varia las etiquetas de"
            if fixme:
                self.fixmes.append(self.new_fixme(feat, fixme))

    def get_fixmes(self):
        nx = gpd.GeoSeries(self.df1.geometry).sindex
        matches = []
        matches1 = []
        for i in self.df2.index:
            g = self.df2.geometry[i]
            candidates = nx.query(g.buffer(0.00001), predicate="intersects")
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

    def new_fixme(self, feat, text):
        msg = text + ' ' + feat.geometry.geom_type
        tags = Diff.clean_tags(feat.tags)
        msg += str(tags)
        return {
            'geom': feat.geometry.point_on_surface(),
            'text': msg,
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
        print(f['geom'], f['text'])


if __name__ == '__main__':
    command()
