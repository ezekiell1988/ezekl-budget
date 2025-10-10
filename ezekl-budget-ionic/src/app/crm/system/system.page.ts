import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonContent } from '@ionic/angular/standalone';

@Component({
  selector: 'app-system',
  templateUrl: './system.page.html',
  styleUrls: ['./system.page.scss'],
  imports: [IonContent, CommonModule]
})
export class SystemPage implements OnInit {

  constructor() { }

  ngOnInit() {
  }

}