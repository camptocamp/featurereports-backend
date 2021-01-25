import http from '../http-common';

class ReportModelApiService {
  getAll() {
    return http.get('/report_models');
  }

  get(id) {
    return http.get(`/report_models/${id}`);
  }

  create(data) {
    return http.post('/report_models', data);
  }

  update(id, data) {
    return http.patch(`/report_models/${id}`, data);
  }

  delete(id) {
    return http.delete(`/report_models/${id}`);
  }
}

export default new ReportModelApiService();
