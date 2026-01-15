/**
 * Modelos para gestión de archivos multimedia
 */

/**
 * Información básica de un archivo multimedia
 */
export interface MediaFile {
  idMediaFile: number;
  nameMediaFile: string;
  pathMediaFile: string;
  urlMediaFile?: string;
  sizeMediaFile: number;
  mimetype: string;
  mediaType: 'image' | 'video' | 'audio' | 'document';
  createAt: string;
}

/**
 * Respuesta al listar archivos multimedia
 */
export interface MediaFileListResponse {
  total: number;
  data: MediaFile[];
}

/**
 * Totales por tipo de medio
 */
export interface MediaTypeTotal {
  mediaType: string;
  quantity: number;
  totalSize: number;
}

/**
 * Totales por año
 */
export interface YearTotal {
  year: number;
  quantity: number;
  totalSize: number;
}

/**
 * Respuesta de totales de archivos multimedia
 */
export interface MediaFileTotalResponse {
  quantity: number;
  totalSize: number;
  mediaType: MediaTypeTotal[];
  byYear: YearTotal[];
}

/**
 * Respuesta al crear un archivo multimedia
 */
export interface MediaFileCreateResponse {
  idMediaFile: number;
  nameMediaFile: string;
  pathMediaFile: string;
  urlMediaFile: string;
}

/**
 * Respuesta al eliminar un archivo multimedia
 */
export interface MediaFileDeleteResponse {
  idMediaFile: number;
}

/**
 * Parámetros para listar archivos
 */
export interface MediaFileListParams {
  search?: string;
  sort?: string;
  page?: number;
  itemPerPage?: number;
  mediaType?: 'image' | 'video' | 'audio' | 'document';
}
