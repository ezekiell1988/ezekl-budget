import { Component, Input, Output, EventEmitter, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonModal,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonIcon,
  IonContent,
  IonSearchbar,
  IonList,
  IonItem,
  IonLabel,
  IonSpinner,
  // IonNote no usado
  ModalController
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { closeOutline, searchOutline, personOutline, businessOutline } from 'ionicons/icons';

import { Subject } from 'rxjs';
import { takeUntil, debounceTime, distinctUntilChanged } from 'rxjs/operators';

import { CrmService } from '../../../services/crm.service';
import { AccountResponse, ContactResponse } from '../../../models/crm.models';

export type CRMEntityType = 'account' | 'contact';

export interface CRMSearchResult {
  id: string;
  name: string;
  subtitle?: string;
  type: CRMEntityType;
  data: AccountResponse | ContactResponse;
}

@Component({
  selector: 'app-crm-search',
  templateUrl: './crm-search.component.html',
  styleUrls: ['./crm-search.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonModal,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonButtons,
    IonButton,
    IonIcon,
    IonContent,
    IonSearchbar,
    IonList,
    IonItem,
    IonLabel,
    IonSpinner
    // IonNote no usado
  ]
})
export class CrmSearchComponent implements OnInit, OnDestroy {
  private crmService = inject(CrmService);
  private destroy$ = new Subject<void>();

  @Input() entityType: CRMEntityType = 'account';
  @Input() isOpen = false;
  @Input() title = 'Buscar';
  @Input() placeholder = 'Buscar...';

  @Output() itemSelected = new EventEmitter<CRMSearchResult>();
  @Output() modalClosed = new EventEmitter<void>();

  searchText = '';
  results: CRMSearchResult[] = [];
  isLoading = false;
  hasSearched = false;

  constructor() {
    addIcons({
      closeOutline,
      searchOutline,
      personOutline,
      businessOutline
    });
  }

  ngOnInit() {
    // Configurar título y placeholder por defecto según el tipo
    if (!this.title || this.title === 'Buscar') {
      this.title = this.entityType === 'account' ? 'Buscar Cuenta' : 'Buscar Contacto';
    }

    if (!this.placeholder || this.placeholder === 'Buscar...') {
      this.placeholder = this.entityType === 'account'
        ? 'Buscar por nombre de empresa...'
        : 'Buscar por nombre de contacto...';
    }
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  async onSearch(event: any) {
    const searchValue = event.target.value?.trim();
    this.searchText = searchValue;

    if (!searchValue || searchValue.length < 2) {
      this.results = [];
      this.hasSearched = false;
      return;
    }

    this.isLoading = true;
    this.hasSearched = true;

    try {
      if (this.entityType === 'account') {
        await this.searchAccounts(searchValue);
      } else {
        await this.searchContacts(searchValue);
      }
    } catch (error) {
      console.error(`Error buscando ${this.entityType}:`, error);
      this.results = [];
    } finally {
      this.isLoading = false;
    }
  }

  private async searchAccounts(searchValue: string) {
    const response = await this.crmService.getAccounts({
      top: 20,
      skip: 0,
      filter_query: `contains(name,'${searchValue}')`,
      select_fields: 'accountid,name,telephone1,emailaddress1,address1_city',
      order_by: 'name asc'
    }).toPromise();

    this.results = response?.accounts.map(account => ({
      id: account.accountid,
      name: account.name,
      subtitle: this.buildAccountSubtitle(account),
      type: 'account' as CRMEntityType,
      data: account
    })) || [];
  }

  private async searchContacts(searchValue: string) {
    const response = await this.crmService.getContacts({
      top: 20,
      skip: 0,
      filter_query: `contains(fullname,'${searchValue}')`,
      select_fields: 'contactid,fullname,emailaddress1,telephone1,jobtitle',
      order_by: 'fullname asc'
    }).toPromise();

    this.results = response?.contacts.map(contact => ({
      id: contact.contactid,
      name: contact.fullname || 'Sin nombre',
      subtitle: this.buildContactSubtitle(contact),
      type: 'contact' as CRMEntityType,
      data: contact
    })) || [];
  }

  private buildAccountSubtitle(account: AccountResponse): string {
    const parts: string[] = [];

    if (account.address1_city) {
      parts.push(account.address1_city);
    }

    if (account.telephone1) {
      parts.push(account.telephone1);
    }

    if (account.emailaddress1) {
      parts.push(account.emailaddress1);
    }

    return parts.join(' • ') || 'Sin información adicional';
  }

  private buildContactSubtitle(contact: ContactResponse): string {
    const parts: string[] = [];

    if (contact.jobtitle) {
      parts.push(contact.jobtitle);
    }

    if (contact.emailaddress1) {
      parts.push(contact.emailaddress1);
    }

    if (contact.telephone1) {
      parts.push(contact.telephone1);
    }

    return parts.join(' • ') || 'Sin información adicional';
  }

  selectItem(result: CRMSearchResult) {
    this.itemSelected.emit(result);
    this.closeModal();
  }

  closeModal() {
    this.searchText = '';
    this.results = [];
    this.hasSearched = false;
    this.modalClosed.emit();
  }

  getEntityIcon(): string {
    return this.entityType === 'account' ? 'business-outline' : 'person-outline';
  }
}
