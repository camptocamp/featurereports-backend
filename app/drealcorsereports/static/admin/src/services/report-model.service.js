import http from '../http-common';

class ReportModelApiService {
  getAll() {
    return http.get('');
  }

  get(id) {
    return http.get(`/${id}`);
  }

  create(data) {
    return http.post('', data);
  }

  update(id, data) {
    return http.patch(`/${id}`, data);
  }

  delete(id) {
    return http.delete(`/${id}`);
  }
}

export default new ReportModelApiService();
