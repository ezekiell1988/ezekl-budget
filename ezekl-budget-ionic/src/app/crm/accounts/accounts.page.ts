import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AppHeaderComponent } from '../../shared/components/app-header/app-header.component';
import {
  IonContent,
  IonButton,
  IonIcon
} from '@ionic/angular/standalone';

@Component({
  selector: 'app-accounts',
  templateUrl: './accounts.page.html',
  styleUrls: ['./accounts.page.scss'],
  imports: [
    CommonModule,
    AppHeaderComponent,
    IonContent,
    IonButton,
    IonIcon
  ]
})
export class AccountsPage implements OnInit {

  constructor() { }

  ngOnInit() {
  }

}
