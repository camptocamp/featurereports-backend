import {httpReportModelService} from '../http-common';

class ReportModelApiService {
  getAll(cancelToken) {
    return httpReportModelService.get('', {
      cancelToken,
    });
  }

  get(id, cancelToken) {
    return httpReportModelService.get(`/${id}`, {
      cancelToken,
    });
  }

  create(data, cancelToken) {
    return httpReportModelService.post('', data, {
      cancelToken,
    });
  }

  update(id, data, cancelToken) {
    const { created_at, created_by, updated_at, updated_by, ...putData } = data;
    return httpReportModelService.put(`/${id}`, putData, {
      cancelToken,
    });
  }

  delete(id, cancelToken) {
    return httpReportModelService.delete(`/${id}`, {
      cancelToken,
    });
  }
}

export default new ReportModelApiService();
