import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AppHeaderComponent } from '../../shared/components/app-header/app-header.component';
import {
  IonContent,
  IonButton,
  IonIcon
} from '@ionic/angular/standalone';

@Component({
  selector: 'app-contacts',
  templateUrl: './contacts.page.html',
  styleUrls: ['./contacts.page.scss'],
  imports: [
    CommonModule,
    AppHeaderComponent,
    IonContent,
    IonButton,
    IonIcon
  ]
})
export class ContactsPage implements OnInit {

  constructor() { }

  ngOnInit() {
  }

}
