/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";

publicWidget.registry.iPushpButton = publicWidget.Widget.extend({
    selector: '.ipushp_container,.check_category, #registration_section',
    events: {
        'click .check_required_fields': '_onCheckRequiredFields',
        'change .select_business_categ': '_onCategory',
        'keyup #myInput': '_onFindCategory',
    },

    _onCheckRequiredFields: function (e) {
        e.preventDefault();
        let flag = 0;
        const field_list = ['business_categ_id', 'relation_id', 'category_id', 'name', 'phone', 'email', 'description'];
        field_list.forEach((field) => {
            const $input = this.$(`[name='${field}']`);
            if ($input.is('select')) {
                if (!$input.val() || $input.val() === '') {
                    $input.css({ 'border': '1px solid red' });
                    flag = 1;
                } else {
                    $input.css({ 'border': '' });
                }
            } else if ($input.is('input')) {
                if ($input.val() === '') {
                    $input.css({ 'border': '1px solid red' });
                    flag = 1;
                } else {
                    $input.css({ 'border': '' });
                }
            }
        });
        const phoneInput = this.$('input[name="phone"]');
        const emailInput = this.$('input[name="email"]');
        const phonePattern = /^[0-9]{10}$/;
        if (phoneInput.val() && !phonePattern.test(phoneInput.val())) {
            phoneInput.css({ 'border': '1px solid red' });
            alert(_t('Please enter a valid 10-digit phone number.'));
            flag = 1;
        }
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (emailInput.val() && !emailPattern.test(emailInput.val())) {
            emailInput.css({ 'border': '1px solid red' });
            alert(_t('Please enter a valid email address.'));
            flag = 1;
        }
        if (flag === 0) {
            const form = this.$('#contact_ipushp_form');
            form.submit();
        } else {
            alert(_t('Please fill in all required fields.'));
        }
    },

    _onCategory: function (ev) {
        if (ev.currentTarget && ev.currentTarget.value == -1) {
            $(".form_so_new_shipp").removeClass("d-none");
            $(".form_so_new_shipp input").prop('required', true);
        } else {
            $(".form_so_new_shipp").addClass("d-none");
            $(".form_so_new_shipp input").prop('required', false);
        }
    },

    _onFindCategory: function () {
        var input, filter, ul, li, a, i, found;
        input = document.getElementById("myInput");
        filter = input.value.toUpperCase();
        ul = document.getElementById("myUL");
        li = ul.getElementsByTagName("li");
        found = false; // Flag to track if any category is found
        for (i = 0; i < li.length; i++) {
            a = li[i].getElementsByTagName("a")[0];
            if (a.innerHTML.toUpperCase().indexOf(filter) > -1) {
                li[i].style.display = "";
                found = true; // Set flag to true if category is found
            } else {
                li[i].style.display = "none";
            }
        }
        // Show message if no category is found
        if (!found) {
            document.getElementById("noResultsMessage").style.display = "block";
        } else {
            document.getElementById("noResultsMessage").style.display = "none";
        }
    }
});