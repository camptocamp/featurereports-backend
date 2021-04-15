import {http, httpLayers} from '../http-common';

class ReportModelApiService {
  getAll(cancelToken) {
    return http.get('', {
      cancelToken,
    });
  }

  get(id, cancelToken) {
    return http.get(`/${id}`, {
      cancelToken,
    });
  }

  getLayers(cancelToken) {
    return httpLayers.get('', {
      cancelToken,
    });
  }

  create(data, cancelToken) {
    return http.post('', data, {
      cancelToken,
    });
  }

  update(id, data, cancelToken) {
    const { created_at, created_by, updated_at, updated_by, ...putData } = data;
    return http.put(`/${id}`, putData, {
      cancelToken,
    });
  }

  delete(id, cancelToken) {
    return http.delete(`/${id}`, {
      cancelToken,
    });
  }
}

export default new ReportModelApiService();
