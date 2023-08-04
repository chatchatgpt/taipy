# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os

import pytest

from src.taipy.core.cycle._cycle_fs_repository import _CycleFSRepository
from src.taipy.core.cycle._cycle_sql_repository import _CycleSQLRepository
from src.taipy.core.cycle.cycle import Cycle, CycleId
from src.taipy.core.exceptions import ModelNotFound


class TestCycleRepositories:
    @pytest.mark.parametrize("repo", [_CycleFSRepository, _CycleSQLRepository])
    def test_save_and_load(self, tmpdir, cycle, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(cycle)

        obj = repository._load(cycle.id)
        assert isinstance(obj, Cycle)

    @pytest.mark.parametrize("repo", [_CycleFSRepository, _CycleSQLRepository])
    def test_exists(self, tmpdir, cycle, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(cycle)

        assert repository._exists(cycle.id)
        assert not repository._exists("not-existed-cycle")

    @pytest.mark.parametrize("repo", [_CycleFSRepository, _CycleSQLRepository])
    def test_load_all(self, tmpdir, cycle, repo):
        repository = repo()
        repository.base_path = tmpdir
        for i in range(10):
            cycle.id = CycleId(f"cycle-{i}")
            repository._save(cycle)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    @pytest.mark.parametrize("repo", [_CycleFSRepository, _CycleSQLRepository])
    def test_load_all_with_filters(self, tmpdir, cycle, repo):
        repository = repo()
        repository.base_path = tmpdir

        for i in range(10):
            cycle.id = CycleId(f"cycle-{i}")
            cycle._name = f"cycle-{i}"
            repository._save(cycle)
        objs = repository._load_all(filters=[{"id": "cycle-2"}])

        assert len(objs) == 1

    @pytest.mark.parametrize("repo", [_CycleSQLRepository])
    def test_delete(self, tmpdir, cycle, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(cycle)

        repository._delete(cycle.id)

        with pytest.raises(ModelNotFound):
            repository._load(cycle.id)

    @pytest.mark.parametrize("repo", [_CycleFSRepository, _CycleSQLRepository])
    def test_delete_all(self, tmpdir, cycle, repo):
        repository = repo()
        repository.base_path = tmpdir

        for i in range(10):
            cycle.id = CycleId(f"cycle-{i}")
            repository._save(cycle)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    @pytest.mark.parametrize("repo", [_CycleFSRepository, _CycleSQLRepository])
    def test_delete_many(self, tmpdir, cycle, repo):
        repository = repo()
        repository.base_path = tmpdir

        for i in range(10):
            cycle.id = CycleId(f"cycle-{i}")
            repository._save(cycle)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    @pytest.mark.parametrize("repo", [_CycleFSRepository, _CycleSQLRepository])
    def test_search(self, tmpdir, cycle, repo):
        repository = repo()
        repository.base_path = tmpdir

        for i in range(10):
            cycle.id = CycleId(f"cycle-{i}")
            cycle.name = f"cycle-{i}"
            repository._save(cycle)

        assert len(repository._load_all()) == 10

        objs = repository._search("name", "cycle-2")
        assert len(objs) == 1
        assert isinstance(objs[0], Cycle)

    @pytest.mark.parametrize("repo", [_CycleFSRepository, _CycleSQLRepository])
    def test_export(self, tmpdir, cycle, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(cycle)

        repository._export(cycle.id, tmpdir.strpath)
        dir_path = repository.dir_path if repo == _CycleFSRepository else os.path.join(tmpdir.strpath, "cycle")
        assert os.path.exists(os.path.join(dir_path, f"{cycle.id}.json"))
