import {httpLayersService} from '../http-common';

class LayerApiService {

  getLayers(cancelToken) {
    return httpLayersService.get('', {
      cancelToken,
    });
  }

}

export default new LayerApiService();