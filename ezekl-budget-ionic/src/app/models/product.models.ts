
/**
 * Modelos para productos
 */

export interface Product {
  idProduct: number;
  nameProduct: string;
  descriptionProduct: string;
  childrens: Product[] | null;
}

export interface ProductResponse {
  total?: number;
  data: Product[];
}

export interface ProductAccountingAccount {
  idProductAccountingAccount: number;
  nameAccountingAccount: string;
  effect: number;
  percent: number;
}

export interface ProductDeliveryPrice {
  idProductDeliveryTypePrice: number;
  nameDeliveryType: string;
  price: number;
}

export interface ProductRequiredSelected {
  idProduct: number;
  nameProduct: string;
}

export interface ProductRequired {
  idProductRequired: number;
  nameProductRequired: string;
  selected: ProductRequiredSelected[] | null;
}

export interface ProductDetail {
  nameProductFather?: string;
  idProductFather?: number;
  idProduct: number;
  nameProduct: string;
  descriptionProduct: string;
  accountingAccount: ProductAccountingAccount[] | null;
  deliveryPrice: ProductDeliveryPrice[] | null;
  required: ProductRequired[] | null;
}
