(this["webpackJsonpweko-facet-search"]=this["webpackJsonpweko-facet-search"]||[]).push([[0],{45:function(e,t,a){},71:function(e,t,a){"use strict";a.r(t);var n=a(0),c=a.n(n),s=a(13),l=a.n(s),i=a(8),r=a(9),o=a(4),d=a(10),u=a(14),h=(a(17),a(18),a(45),a(29)),b=a(6),m=a(73),p=a(40),v=a(3);var j=function(e){for(var t=e.values,a=e.name,n=e.labels,c=window.location.search.replace(",","%2C")||"?",s=window.location.search.substring(1).split("&"),l=0;l<s.length;l++)s[l]=decodeURIComponent(s[l]);var i=[],r=[];return t&&t.map((function(e,t){var c={label:(n[e.key]||e.key)+"("+e.doc_count+")",value:e.key};r.push(c);var l=a+"="+e.key;-1!=s.indexOf(l)&&i.push(c)})),Object(v.jsx)("div",{children:Object(v.jsx)("div",{className:"select-container",children:Object(v.jsx)(p.a,{defaultValue:i,isMulti:!0,name:"Facet_Search",ontrolShouldRenderValue:!1,onChange:function(e){!function(e){var t="";if(c.indexOf("&")>=0){for(var n=c.split("&"),s=0;s<n.length;s++)n[s].indexOf(encodeURIComponent(a)+"=")<0&&(t+="&"+n[s]);t=t.substring(1)}""!=t&&(c=t),e.map((function(e,t){var n=encodeURIComponent(a)+"="+encodeURIComponent(e.value);c+="&"+n})),c=c.replace("q=0","q="),c+=-1==c.indexOf("is_facet_search=")?"&is_facet_search=true":"",window.location.href="/search"+c}(e)},backspaceRemovesValue:!1,isClearable:!1,options:r,className:"basic-multi-select",classNamePrefix:"select"})})})},f=a(39);var g=function(e){var t=e.value,a=(e.name,e.labels);function c(e){var t=new RegExp(/^(\d{8})|(\d{6})|(\d{4})$/).exec(e),a=!1;return t.length>0&&e==t[0]&&(a=!0),a}var s,l,i={},r=[],o=window.location.search.replace(",","%2C")||"?";if(t&&t.map((function(e,t){var a;e.key.length>0&&(a=parseInt(e.key),r.push(a))})),r.length>1)for(l in r.sort(),s=100/((r=Array.from(new Set(r))).length-1),r)i[l*s]=r[l].toString();var d=Object(n.useState)(r[0]),u=Object(b.a)(d,2),h=u[0],m=u[1],p=Object(n.useState)(r[l]),j=Object(b.a)(p,2),g=j[0],O=j[1];return Object(v.jsxs)("div",{children:[Object(v.jsx)("div",{className:"col-sm-11",style:{paddingBottom:"20px","white-space":"nowrap"},children:Object(v.jsx)(f.a.Range,{min:0,marks:i,step:s,onChange:function(e){m(i[e[0]]),O(i[e[1]])},defaultValue:[0,100]})}),Object(v.jsxs)("div",{className:"form-group row",children:[Object(v.jsx)("div",{className:"col-sm-5",children:Object(v.jsx)("input",{type:"number",id:"input_head",className:"form-control",value:h,onChange:function(e){return m(e.target.value)}})}),Object(v.jsx)("div",{className:"col-sm-5",children:Object(v.jsx)("input",{type:"number",id:"input_tail",className:"form-control",value:g,onChange:function(e){return O(e.target.value)}})}),Object(v.jsx)("div",{className:"col-sm-2",children:Object(v.jsxs)("button",{type:"button",style:{marginLeft:"3px"},className:"btn btn-primary pull-right",onClick:function(){!function(){var e="";if(o.indexOf("&")>=0){var t=o.split("&");console.log(t);for(var a=0;a<t.length;a++)t[a].indexOf(encodeURIComponent("date_range1_from")+"=")<0&&t[a].indexOf(encodeURIComponent("date_range1_to")+"=")<0&&(e+="&"+t[a]);e=e.substring(1)}""!=e&&(o=e)}();var e=parseInt(h),t=parseInt(g),a="";e&&c(e)&&(a+="&"+encodeURIComponent("date_range1_from")+"="+encodeURIComponent(e)),t&&c(t)&&(a+="&"+encodeURIComponent("date_range1_to")+"="+encodeURIComponent(t)),a&&(o+=a,window.location.href="/search"+o)},children:[" ",a.Goto]})})]})]})};var O=function(e){var t=e.values,a=e.name,n=e.labels,c=e.displayNumber,s="id_"+a+"_chkbox",l=s.replace(" ","\\ "),i=function(e){var t=e.id,a=e.value,n=e.checked,c=e.onChange;return null!=c?Object(v.jsx)("input",{id:t,className:"facet-chbox",type:"checkbox",checked:n,onChange:c,value:a}):Object(v.jsx)("input",{id:t,className:"facet-chbox",type:"checkbox",defaultChecked:n,value:a})},r=function(e){var t=e.values,a=e.name,n=e.isModal,c=e.displayNumber,s=e.onChange;return t.map((function(e,t){if(n||t<c){var l="id_"+a+(n?"_chkbox_mdl_":"_chkbox_")+t,r=e.key+"("+e.doc_count+")",o=-1!=m.indexOf(a+"="+e.key);return Object(v.jsx)("div",{children:Object(v.jsxs)("label",{htmlFor:l,children:[Object(v.jsx)(i,{id:l,value:e.key,checked:o,onChange:s},l),r]})},l)}}))},o=function(e){var t=e.values,a=e.name,c=e.modalId;return Object(v.jsxs)("div",{className:"chbox-mdl",id:c,children:[Object(v.jsx)("a",{href:"#!",className:"overlay",onClick:d,modalId:c}),Object(v.jsx)("div",{className:"window",children:Object(v.jsxs)("div",{className:"content",children:[Object(v.jsx)("div",{className:"list",children:Object(v.jsx)(r,{values:t,name:a,isModal:!0})}),Object(v.jsxs)("div",{className:"footer",children:[Object(v.jsx)("a",{href:"#!",onClick:d,modalId:c,children:n.cancel}),Object(v.jsx)("button",{type:"button",className:"btn btn-primary",onClick:u,children:n.search})]})]})})]},c)};function d(e){null!=e&&document.getElementById(e.target.getAttribute("modalId")).classList.remove("is-active")}function u(e){var t=[];document.querySelector("#"+l).querySelectorAll(".chbox-mdl input").forEach((function(e){e.checked&&t.push({label:a,value:e.value})})),h(t)}function h(e){var t="";if(b.indexOf("&")>=0){for(var n=b.split("&"),c=0;c<n.length;c++)n[c].indexOf(encodeURIComponent(a)+"=")<0&&(t+="&"+n[c]);t=t.substring(1)}""!=t&&(b=t),e.map((function(e,t){var n=encodeURIComponent(a)+"="+encodeURIComponent(e.value);b+="&"+n})),b=b.replace("q=0","q="),b+=-1==b.indexOf("is_facet_search=")?"&is_facet_search=true":"",window.location.href="/search"+b}for(var b=window.location.search.replace(",","%2C")||"?",m=window.location.search.substring(1).split("&"),p=0;p<m.length;p++)m[p]=decodeURIComponent(m[p]);var j="id_"+a+"_checkbox_modal",f=null==c?5:c;return Object(v.jsx)("div",{id:s,children:Object(v.jsxs)("div",{className:"chbox-container",children:[Object(v.jsx)(r,{values:t,name:a,isModal:!1,displayNumber:f,onChange:function(e){var t=[];document.querySelector("#"+l).querySelectorAll(".chbox-mdl input").forEach((function(n){(n.checked&&e.target.value!==n.value||e.target.checked&&e.target.value===n.value)&&t.push({label:a,value:n.value})})),h(t)}}),t.length>f&&Object(v.jsx)("a",{href:"#"+j,onClick:function(e){null!=e?(document.getElementById(e.target.getAttribute("modalId")).classList.add("is-active"),document.querySelector("#"+l).querySelectorAll(".chbox-mdl input").forEach((function(e){e.checked=-1!=m.indexOf(a+"="+e.value)}))):console.log("event == null")},modalId:j,children:". . . See More"}),Object(v.jsx)(o,{values:t,name:a,modalId:j,displayNumber:c})]})})};for(var x=function(e){var t=e.item,a=e.nameshow,c=e.name,s=e.key,l=e.labels,i=e.isInitOpen,r=e.uiType,o=e.displayNumber,d=window.location.search.replace(",","%2C").indexOf(encodeURIComponent(c))>=0||i,u=Object(n.useState)(d),h=Object(b.a)(u,2),p=h[0],f=h[1];return Object(v.jsxs)("div",{className:"panel panel-default",children:[Object(v.jsxs)("div",{className:"panel-heading clearfix",children:[Object(v.jsx)("h3",{className:"panel-title pull-left",children:a}),Object(v.jsxs)("a",{className:"pull-right",onClick:function(){return f(!p)},children:[!p&&Object(v.jsx)("span",{children:Object(v.jsx)("i",{className:"glyphicon glyphicon-chevron-right"})}),p&&Object(v.jsx)("span",{children:Object(v.jsx)("i",{className:"glyphicon glyphicon-chevron-down"})})]})]}),Object(v.jsx)(m.a,{isOpen:p,children:Object(v.jsxs)("div",{className:"panel-body index-body",children:[null!=t&&"SelectBox"===r&&Object(v.jsx)(j,{values:t.buckets,name:c,labels:l}),null!=t&&"CheckboxList"===r&&Object(v.jsx)(O,{values:t.buckets,name:c,labels:l,displayNumber:o}),null!=t&&"RangeSlider"===r&&Object(v.jsx)(g,{value:t.buckets,name:c,labels:l})]})})]},s)},y={},k=document.getElementsByClassName("body-facet-search-label"),_=0;_<k.length;_++)y[k[_].id]=k[_].value;var C=function(e){Object(d.a)(a,e);var t=Object(u.a)(a);function a(e){var n;return Object(i.a)(this,a),(n=t.call(this,e)).state={is_enable:!1,list_title:{},list_facet:{},list_order:{},list_uiType:{},list_isOpen:{},list_displayNumber:{}},n.getTitleAndOrder=n.getTitleAndOrder.bind(Object(o.a)(n)),n.get_facet_search_list=n.get_facet_search_list.bind(Object(o.a)(n)),n.convertData=n.convertData.bind(Object(o.a)(n)),n}return Object(r.a)(a,[{key:"getTitleAndOrder",value:function(){var e=this,t={},a={},n={},c={},s={};Object(h.a)("/facet-search/get-title-and-order",{method:"POST"}).then((function(e){return e.json()})).then((function(l){l.status&&(t=l.data.titles,a=l.data.order,n=l.data.uiTypes,c=l.data.isOpens,s=l.data.displayNumbers),e.setState({list_title:t}),e.setState({list_order:a}),e.setState({list_uiType:n}),e.setState({list_isOpen:c}),e.setState({list_displayNumber:s}),e.setState({is_enable:!0})}))}},{key:"get_facet_search_list",value:function(){var e=this,t=new URLSearchParams(window.location.search),a=2==t.get("search_type")?"/api/index/":"/api/records/";Object(h.a)(a+"?"+t.toString()).then((function(e){return e.json()})).then((function(a){if(2==t.get("search_type")){var n=a&&a.aggregations&&a.aggregations.aggregations?a.aggregations.aggregations[0]:{};e.convertData(n)}else e.convertData(a&&a.aggregations?a.aggregations:{})}))}},{key:"convertData",value:function(e){var t={};e&&Object.keys(e).map((function(a,n){var c=e[a][a]?e[a][a]:e[a],s=c.key&&c.key.hasOwnProperty("buckets");if(s=c.hasOwnProperty("buckets")||s){if(t[a]=c[a]?c[a]:c,"Time Period(s)"!=a&&"Data Language"!=a&&"Access"!=a)for(var l=document.getElementById("lang-code"),i=l.options[l.selectedIndex].value,r=t[a],o=0;o<r.buckets.length;o++){var d=r.buckets[o];("en"==i&&(d.key.charCodeAt(0)>256||d.key.charCodeAt(d.key.length-1)>256)||"en"!=i&&d.key.charCodeAt(0)<256&&d.key.charCodeAt(d.key.length-1)<256)&&(t[a].buckets.splice(o,1),o--)}if("Access"==a)for(var u=t[a],h=0;h<u.buckets.length;h++){var b=u.buckets[h];(b.key.charCodeAt(0)>256||b.key.charCodeAt(b.key.length-1)>256)&&(t[a].buckets.splice(h,1),h--)}}})),this.setState({list_facet:t})}},{key:"componentDidMount",value:function(){this.getTitleAndOrder(),this.get_facet_search_list()}},{key:"render",value:function(){var e=this.state,t=e.is_enable,a=e.list_title,n=e.list_facet,c=e.list_order,s=e.list_uiType,l=e.list_isOpen,i=e.list_displayNumber;return Object(v.jsx)("div",{children:t&&Object(v.jsx)("div",{className:"facet-search break-word",children:Object.keys(c).map((function(e,t){var r=c[e],o=n[r],d=a[r],u=l[r],h=s[r],b=i[r];return Object(v.jsx)(x,{item:o,nameshow:d,name:r,labels:y,isInitOpen:u,uiType:h,displayNumber:b},t)}))})})}}]),a}(c.a.Component);l.a.render(Object(v.jsx)(c.a.StrictMode,{children:Object(v.jsx)(C,{})}),document.getElementById("app-facet-search"))}},[[71,1,2]]]);
//# sourceMappingURL=main.36ae1210.chunk.js.map