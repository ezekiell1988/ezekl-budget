/**
 * Modelos para la API de ClickEat
 */

// ========== Address Models ==========

export interface CustomerAddressAddRequest {
  address: string;
  latitude: number;
  longitude: number;
}

export interface CustomerAddressAddResponse {
  idAddress: number;
  address?: string;
  latitude?: number;
  longitude?: number;
}

// ========== Restaurant Models ==========

export interface RestaurantClosestByAddressResponse {
  success: boolean;
  message: string;
  idRestaurant?: number;
  nameRestaurant?: string;
  distance?: number;
}

// ========== Delivery Types ==========

export interface DeliveryTypeItem {
  idDeliveryType: string;
  nameDeliveryType: string;
}

// ========== Payment Types ==========

export interface PaymentTypeItem {
  idPaymentType: number;
  namePaymentType: string;
}

export interface PaymentTypeResponse {
  success: boolean;
  message: string;
  paymentTypes: PaymentTypeItem[];
}

// ========== Customer Models ==========

export interface CustomerAddress {
  idAddress: number;
  address: string;
  latitude: number;
  longitude: number;
  isDefault: boolean;
}

export interface CustomerResponse {
  success: boolean;
  message: string;
  idCustomer?: number;
  nameCustomer?: string;
  phone?: string;
  email?: string;
  addresses?: CustomerAddress[];
}

// ========== Product Models ==========

export interface ProductItem {
  idProduct: number;
  nameProduct: string;
  descriptionProduct: string;
  price: number;
  imageUrl?: string;
}

export interface ProductCategory {
  idCategory: number;
  nameCategory: string;
  products: ProductItem[];
}

export interface ProductMenuResponse {
  success: boolean;
  message: string;
  categories: ProductCategory[];
}

// ========== Shop Cart Models ==========

export interface ShopCartItem {
  idProduct: number;
  nameProduct: string;
  quantity: number;
  price: number;
  total: number;
  options?: any[];
}

export interface ShopCartResponse {
  success: boolean;
  message: string;
  items: ShopCartItem[];
  itemCount: number;
  total: number;
}

// ========== Invoice Models ==========

export interface CreateInvoiceRequest {
  idAddress: number;
  idDeliveryType: string;
  idRestaurant: number;
  idPaymentType: number;
}

export interface CreateInvoiceResponse {
  success: boolean;
  message: string;
  idInvoice?: number;
  invoiceHash?: string;
  total?: number;
}
