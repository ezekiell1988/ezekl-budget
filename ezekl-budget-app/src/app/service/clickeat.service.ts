import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  CustomerAddressAddRequest,
  CustomerAddressAddResponse,
  RestaurantClosestByAddressResponse,
  DeliveryTypeItem,
  PaymentTypeResponse,
  CustomerResponse,
  ProductMenuResponse,
  ShopCartResponse,
  CreateInvoiceRequest,
  CreateInvoiceResponse,
} from '../shared/models';

@Injectable({
  providedIn: 'root'
})
export class ClickeatService {
  private apiUrl = environment.apiUrl;
  private merchantId = 1; // ID del merchant por defecto

  constructor(private http: HttpClient) {}

  /**
   * Construir URL base para los endpoints de Clickeat
   */
  private getBaseUrl(phone: string): string {
    return `${this.apiUrl}clickeat/${phone}`;
  }

  /**
   * Obtener tipos de entrega disponibles
   */
  getDeliveryTypes(phone: string): Observable<DeliveryTypeItem[]> {
    const url = `${this.getBaseUrl(phone)}/delivery-types.json`;
    return this.http.get<DeliveryTypeItem[]>(url);
  }

  /**
   * Obtener información del cliente por teléfono
   */
  getCustomer(phone: string, idDeliveryType: string): Observable<CustomerResponse> {
    const url = `${this.getBaseUrl(phone)}/customer.json?idDeliveryType=${idDeliveryType}`;
    return this.http.get<CustomerResponse>(url);
  }

  /**
   * Agregar una nueva dirección para el cliente
   */
  addressAdd(phone: string, addressData: CustomerAddressAddRequest): Observable<CustomerAddressAddResponse> {
    const url = `${this.getBaseUrl(phone)}/address`;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'accept': 'application/json'
    });
    return this.http.post<CustomerAddressAddResponse>(url, addressData, { headers });
  }

  /**
   * Obtener restaurante más cercano por dirección
   */
  getClosestRestaurant(phone: string, idAddress: number): Observable<RestaurantClosestByAddressResponse> {
    const url = `${this.getBaseUrl(phone)}/address/${idAddress}/restaurants/closest.json`;
    return this.http.get<RestaurantClosestByAddressResponse>(url);
  }

  /**
   * Obtener restaurantes para pick-up
   */
  getRestaurantsPickup(
    phone: string,
    page: number = 1,
    rowsPerPage: number = 100,
    sort: string = 'nameRestaurant_asc'
  ): Observable<any> {
    const url = `${this.getBaseUrl(phone)}/restaurants/pickup.json?page=${page}&rowsPerPage=${rowsPerPage}&sort=${sort}`;
    return this.http.get<any>(url);
  }

  /**
   * Obtener promociones diarias
   */
  getDailyPromos(phone: string, idDeliveryType: string, idRestaurant: number): Observable<ProductMenuResponse> {
    const url = `${this.getBaseUrl(phone)}/products/daily-promos.json?idDeliveryType=${idDeliveryType}&idRestaurant=${idRestaurant}`;
    return this.http.get<ProductMenuResponse>(url);
  }

  /**
   * Obtener menú de productos
   */
  getProductMenu(phone: string, idDeliveryType: string, idRestaurant: number): Observable<ProductMenuResponse> {
    const url = `${this.getBaseUrl(phone)}/products/menu.json?idDeliveryType=${idDeliveryType}&idRestaurant=${idRestaurant}`;
    return this.http.get<ProductMenuResponse>(url);
  }

  /**
   * Obtener carrito de compras
   */
  getCart(phone: string): Observable<ShopCartResponse> {
    const url = `${this.getBaseUrl(phone)}/cart.json`;
    return this.http.get<ShopCartResponse>(url);
  }

  /**
   * Limpiar carrito de compras
   */
  clearCart(phone: string): Observable<ShopCartResponse> {
    const url = `${this.getBaseUrl(phone)}/cart`;
    return this.http.delete<ShopCartResponse>(url);
  }

  /**
   * Eliminar item del carrito
   */
  removeCartItem(phone: string, idProduct: number): Observable<ShopCartResponse> {
    const url = `${this.getBaseUrl(phone)}/cart/items/${idProduct}`;
    return this.http.delete<ShopCartResponse>(url);
  }

  /**
   * Obtener tipos de pago
   */
  getPaymentTypes(phone: string): Observable<PaymentTypeResponse> {
    const url = `${this.getBaseUrl(phone)}/payment-types.json`;
    return this.http.get<PaymentTypeResponse>(url);
  }

  /**
   * Crear factura
   */
  createInvoice(phone: string, invoiceData: CreateInvoiceRequest): Observable<CreateInvoiceResponse> {
    const url = `${this.getBaseUrl(phone)}/invoice`;
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'accept': 'application/json'
    });
    return this.http.post<CreateInvoiceResponse>(url, invoiceData, { headers });
  }
}
