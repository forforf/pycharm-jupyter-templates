import copy
import re
from collections import defaultdict
from pathlib import Path

import nbformat as nbf

NBF_VERSION = 4

NBTPLT = 'nbtplt'
NBTPLT_CELL_TYPES = defaultdict(lambda: 'code')
NBTPLT_CELL_TYPES['md'] = 'markdown'


class NbTpltSrc:

    @classmethod
    def get_pycharm_metadata(cls, cell):
        pycharm_metadata = None
        try:
            cell_md = cell.metadata
            pycharm_metadata = cell_md.pycharm
        except AttributeError:
            # Don't throw so we can return value
            pass
        return pycharm_metadata

    @classmethod
    def get_pycharm_name(cls, cell):
        """
        Note all pycharm cells will have a pycharm name
        """
        name = None
        md = cls.get_pycharm_metadata(cell)
        try:
            name = md.name
        except AttributeError:
            # Don't throw so we can return value
            pass
        return name

    @classmethod
    def _get_nbtplt_from_name(cls, pycharm_name):
        if pycharm_name is None:
            return None
        pattern = r'nbtplt\s(.+?)$'
        m = re.search(pattern, pycharm_name)
        return m.group(1) if m else None

    @classmethod
    def _split_tplt_label(cls, label):
        if label is None:
            return label
        cid, _sep, ctype = label.partition(' ')
        return cid, ctype

    @classmethod
    def _set_metadata(cls, cell_id, cell_label):
        return {NBTPLT: {
            'id': cell_id,
            'label': cell_label
        }}

    @classmethod
    def get_nbtplt(cls, cell):
        label = cls._get_nbtplt_from_name(cls.get_pycharm_name(cell))
        return cls._split_tplt_label(label)

    @classmethod
    def update_map(cls, raw_map):
        _mapping = {}
        for nb_k, nb_v in raw_map.items():
            cid, ctype = nb_k
            cell_type = NBTPLT_CELL_TYPES[ctype]
            nb_v['cell_type'] = cell_type
            nb_v['metadata'] = {} | nb_v['metadata'] | cls._set_metadata(cid, ctype)
            _mapping[cid] = nb_v
        return _mapping

    def __init__(self, path):
        self.path = path
        self.nb = nbf.read(self.path, as_version=NBF_VERSION)
        # We keep placeholders (None) for the non-templated cells self.nbtplts is the same size as self.nb.cells
        self.nbtplts = [self.get_nbtplt(c) for c in self.nb.cells]
        # map holds the source cells (with updated metadata)
        self.map = self.update_map(self._get_raw_map())
        assert len(self.nbtplts) == len(self.nb.cells)

    def _get_raw_map(self):
        _raw_mapping = {}
        for cid, cdata in zip(self.nbtplts, self.nb.cells):
            if cid is None:
                continue
            _raw_mapping[cid] = cdata
        return _raw_mapping


class NbTpltGen(NbTpltSrc):

    def __init__(self, template_path):
        self.tplt_path = template_path
        super().__init__(template_path)

    def _get_dest_index(self, key):
        matched_indices = [i for i, t in enumerate(self.nbtplts) if t and t[0] == key]
        assert len(matched_indices) == 1
        return matched_indices[0]

    def update_cells(self, src):
        dest_cells = copy.deepcopy(self.nb.cells)
        # Cells where the template should be applied will have matching keys
        matching_keys = list(set(self.map.keys()) & set(src.map.keys()))
        for k in matching_keys:
            dest_cell_index = self._get_dest_index(k)
            src_cell_data = src.map[k]
            dest_cells[dest_cell_index] = src_cell_data
        return dest_cells


class NbTpltChain:
    def __init__(self, dest_path_prefix, template_path, src_paths):
        self.dest_path_prefix = dest_path_prefix
        self.template_path = template_path
        self.src_paths = src_paths
        self.srcs = [NbTpltSrc(src) for src in self.src_paths]
        self.template = NbTpltGen(template_path)

    def generate(self):
        for src in self.srcs:
            new_nb = copy.deepcopy(self.template.nb)
            new_nb['cells'] = self.template.update_cells(src)
            src_basename = Path(src.path).name
            fname = f'{self.dest_path_prefix}{src_basename}'
            with open(fname, 'w') as f:
                nbf.write(new_nb, f)
