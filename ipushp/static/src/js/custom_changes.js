 /** @odoo-module **/

 import publicWidget from "@web/legacy/js/public/public_widget";

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
         const field_list = ['business_categ_id', 'relation_id', 'name', 'phone', 'email', 'description'];
 
       
         field_list.forEach((field) => {
             const $input = this.$(`input[name='${field}']`); 
             if ($input.val() === '') {
                 $input.css({ 'border': '1px solid red' });
                 flag = 1; 
             } else {
                 $input.css({ 'border': '' }); 
             }
 
         });
         if (flag === 0) {
            const form = this.$('#contact_ipushp_form'); 
            form.submit(); 
        } else {   
            alert('Please fill in all required fields.');  
        }
       
 
     },

     _onCategory: function(ev){

       
        if ( ev.currentTarget && ev.currentTarget.value == -1) {
            $(".form_so_new_shipp").removeClass("d-none");
            $(".form_so_new_shipp input").prop('required', true);
        } else {
            $(".form_so_new_shipp").addClass("d-none");
            $(".form_so_new_shipp input").prop('required', false);
        }

     },

     _onFindCategory: function(){

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