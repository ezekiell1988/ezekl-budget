import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PanelComponent } from '../../components/panel/panel.component';

@Component({
  selector: 'home',
  templateUrl: './home.html',
  standalone: true,
  imports: [CommonModule, PanelComponent]
})

export class HomePage {
}
