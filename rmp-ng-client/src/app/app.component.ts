import { Component, OnInit, OnDestroy } from '@angular/core';
import { Observable } from "rxjs/Observable";
import { Subscription } from "rxjs/Subscription";
import { FormGroup, FormControl, FormBuilder } from "@angular/forms";

import { RMPConfig } from './services/rmp.config';
import { RMPService } from './services/rmp.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  private subs: Subscription[] = [];
  title = 'Raiden Micropayments Service Client';
  accounts: string[];
  form: FormGroup;
  signed$: Observable<string>;

  constructor(private config: RMPConfig,
              private rmp: RMPService,
              private fb: FormBuilder) {
    this.form = this.fb.group({
      account: '',
      message: null,
    })
  }

  ngOnInit() {
    this.accounts = this.rmp.getAccounts();
  }

  ngOnDestroy() {
    this.subs.forEach((s) => s.unsubscribe());
  }

  onFormSubmit() {
    console.log("B", this.form.value);
    this.signed$ = this.rmp.signMessage(this.form.value.message, this.form.value.account);
  }
}