 /* 
  * アップデートする制限公開アイテムタイプのIDを指定します。
  * 30015は例です。
  */

--schema
UPDATE public.item_type_property
SET schema = 
'{
    "format": "object",
    "properties": {
        "accessdate": {
            "format": "datetime",
            "title": "公開日",
            "title_i18n": {
                "en": "",
                "ja": ""
            },
            "type": "string"
        },
        "accessrole": {
            "default": "open_restricted",
            "enum": [
                "open_access",
                "open_date",
                "open_login",
                "open_no",
                "open_restricted"
            ],
            "format": "radios",
            "title": "アクセス",
            "type": "string"
        },
        "displaytype": {
            "enum": [
                "detail",
                "simple",
                "preview"
            ],
            "format": "select",
            "title": "表示形式",
            "type": "string"
        },
        "fileDate": {
            "format": "array",
            "items": {
                "format": "object",
                "properties": {
                    "fileDateType": {
                        "currentEnum": [
                            "Accepted",
                            "Collected",
                            "Copyrighted",
                            "Issued",
                            "Submitted",
                            "Updated",
                            "Valid"
                        ],
                        "enum": [
                            null,
                            "Accepted",
                            "Collected",
                            "Copyrighted",
                            "Issued",
                            "Submitted",
                            "Updated",
                            "Valid"
                        ],
                        "format": "select",
                        "title": "日付タイプ",
                        "type": [
                            "null",
                            "string"
                        ]
                    },
                    "fileDateValue": {
                        "format": "datetime",
                        "title": "日付",
                        "title_i18n": {
                            "en": "",
                            "ja": ""
                        },
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "title": "日付",
            "type": "array"
        },
        "filename": {
            "enum": [],
            "format": "select",
            "title": "表示名",
            "type": "string"
        },
        "filesize": {
            "format": "array",
            "items": {
                "format": "object",
                "properties": {
                    "value": {
                        "format": "text",
                        "title": "サイズ",
                        "title_i18n": {
                            "en": "",
                            "ja": ""
                        },
                        "type": "string"
                    }
                },
                "type": "object"
            },
            "title": "サイズ",
            "type": "array"
        },
        "format": {
            "format": "text",
            "title": "フォーマット",
            "title_i18n": {
                "en": "",
                "ja": ""
            },
            "type": "string"
        },
        "licensefree": {
            "format": "textarea",
            "title": " ",
            "title_i18n": {
                "en": "",
                "ja": ""
            },
            "type": "string"
        },
        "licensetype": {
            "enum": [],
            "format": "select",
            "title": "ライセンス",
            "type": "string"
        },
        "provide": {
            "format": "array",
            "items": {
                "format": "object",
                "properties": {
                    "role": {
                        "currentEnum": [],
                        "enum": [],
                        "format": "select",
                        "title": "ロール",
                        "type": [
                            "string",
                            "number",
                            "null"
                        ]
                    },
                    "workflow": {
                        "currentEnum": [],
                        "enum": [],
                        "format": "select",
                        "title": "ワークフロー",
                        "type": [
                            "string",
                            "number",
                            "null"
                        ]
                    }
                },
                "type": "object"
            },
            "title": "提供方法",
            "type": "array"
        },
        "roles": {
            "format": "array",
            "items": {
                "format": "object",
                "properties": {
                    "role": {
                        "currentEnum": [],
                        "enum": [],
                        "format": "select",
                        "title": "ロール",
                        "type": [
                            "string",
                            "number",
                            "null"
                        ]
                    }
                },
                "type": "object"
            },
            "title": "ロール",
            "type": "array"
        },
        "terms": {
            "enum": [],
            "format": "select",
            "title": "利用規約",
            "type": [
                "string",
                "number",
                "null"
            ]
        },
        "termsDescription": {
            "format": "textarea",
            "title": " ",
            "title_i18n": {
                "en": "",
                "ja": ""
            },
            "type": "string"
        },
        "url": {
            "format": "object",
            "properties": {
                "label": {
                    "format": "text",
                    "title": "ラベル",
                    "title_i18n": {
                        "en": "",
                        "ja": ""
                    },
                    "type": "string"
                },
                "objectType": {
                    "currentEnum": [
                        "abstract",
                        "dataset",
                        "fulltext",
                        "software",
                        "summary",
                        "thumbnail",
                        "other"
                    ],
                    "enum": [
                        null,
                        "abstract",
                        "dataset",
                        "fulltext",
                        "software",
                        "summary",
                        "thumbnail",
                        "other"
                    ],
                    "format": "select",
                    "title": "オブジェクトタイプ",
                    "type": "string"
                },
                "url": {
                    "format": "text",
                    "title": "本文URL",
                    "title_i18n": {
                        "en": "",
                        "ja": ""
                    },
                    "type": "string"
                }
            },
            "title": "本文URL",
            "type": "object"
        },
        "version": {
            "format": "text",
            "title": "バージョン情報",
            "title_i18n": {
                "en": "",
                "ja": ""
            },
            "type": "string"
        }
    },
    "type": "object"
}'::jsonb
WHERE id=30015;

--form
UPDATE public.item_type_property
SET form = '
{
    "items": [
        {
            "key": "parentkey.filename",
            "onChange": "fileNameSelect(this, form, modelValue)",
            "templateUrl": "/static/templates/weko_deposit/datalist.html",
            "title": "表示名",
            "titleMap": [],
            "title_i18n": {
                "en": "FileName",
                "ja": "表示名"
            },
            "type": "template"
        },
        {
            "items": [
                {
                    "disableSuccessState": true,
                    "feedback": false,
                    "fieldHtmlClass": "file-text-url",
                    "key": "parentkey.url.url",
                    "title": "本文URL",
                    "title_i18n": {
                        "en": "Text URL",
                        "ja": "本文URL"
                    },
                    "type": "text"
                },
                {
                    "disableSuccessState": true,
                    "feedback": false,
                    "key": "parentkey.url.label",
                    "title": "ラベル",
                    "title_i18n": {
                        "en": "Label",
                        "ja": "ラベル"
                    },
                    "type": "text"
                },
                {
                    "disableSuccessState": true,
                    "feedback": false,
                    "key": "parentkey.url.objectType",
                    "title": "オブジェクトタイプ",
                    "titleMap": [
                        {
                            "name": "abstract",
                            "name_i18n": {
                                "en": "abstract",
                                "ja": "abstract"
                            },
                            "value": "abstract"
                        },
                        {
                            "name": "dataset",
                            "name_i18n": {
                                "en": "dataset",
                                "ja": "dataset"
                            },
                            "value": "dataset"
                        },
                        {
                            "name": "fulltext",
                            "name_i18n": {
                                "en": "fulltext",
                                "ja": "fulltext"
                            },
                            "value": "fulltext"
                        },
                        {
                            "name": "software",
                            "name_i18n": {
                                "en": "software",
                                "ja": "software"
                            },
                            "value": "software"
                        },
                        {
                            "name": "summary",
                            "name_i18n": {
                                "en": "summary",
                                "ja": "summary"
                            },
                            "value": "summary"
                        },
                        {
                            "name": "thumbnail",
                            "name_i18n": {
                                "en": "thumbnail",
                                "ja": "thumbnail"
                            },
                            "value": "thumbnail"
                        },
                        {
                            "name": "other",
                            "name_i18n": {
                                "en": "other",
                                "ja": "other"
                            },
                            "value": "other"
                        }
                    ],
                    "title_i18n": {
                        "en": "Object Type",
                        "ja": "オブジェクトタイプ"
                    },
                    "type": "select"
                }
            ],
            "key": "parentkey.url",
            "title": "本文URL",
            "title_i18n": {
                "en": "Text URL",
                "ja": "本文URL"
            },
            "type": "fieldset"
        },
        {
            "key": "parentkey.format",
            "title": "フォーマット",
            "title_i18n": {
                "en": "Format",
                "ja": "フォーマット"
            },
            "type": "text"
        },
        {
            "add": "New",
            "items": [
                {
                    "key": "parentkey.filesize[].value",
                    "title": "サイズ",
                    "title_i18n": {
                        "en": "Size",
                        "ja": "サイズ"
                    },
                    "type": "text"
                }
            ],
            "key": "parentkey.filesize",
            "style": {
                "add": "btn-success"
            },
            "title": "サイズ",
            "title_i18n": {
                "en": "Size",
                "ja": "サイズ"
            }
        },
        {
            "add": "New",
            "items": [
                {
                    "key": "parentkey.fileDate[].fileDateType",
                    "title": "日付タイプ",
                    "titleMap": [
                        {
                            "name": "Accepted",
                            "value": "Accepted"
                        },
                        {
                            "name": "Collected",
                            "value": "Collected"
                        },
                        {
                            "name": "Copyrighted",
                            "value": "Copyrighted"
                        },
                        {
                            "name": "Issued",
                            "value": "Issued"
                        },
                        {
                            "name": "Submitted",
                            "value": "Submitted"
                        },
                        {
                            "name": "Updated",
                            "value": "Updated"
                        },
                        {
                            "name": "Valid",
                            "value": "Valid"
                        }
                    ],
                    "title_i18n": {
                        "en": "Date Type",
                        "ja": "日付タイプ"
                    },
                    "type": "select"
                },
                {
                    "format": "yyyy-MM-dd",
                    "key": "parentkey.fileDate[].fileDateValue",
                    "templateUrl": "/static/templates/weko_deposit/datepicker.html",
                    "title": "日付",
                    "title_i18n": {
                        "en": "Date",
                        "ja": "日付"
                    },
                    "type": "template"
                }
            ],
            "key": "parentkey.fileDate",
            "style": {
                "add": "btn-success"
            },
            "title": "日付",
            "title_i18n": {
                "en": "Date",
                "ja": "日付"
            }
        },
        {
            "key": "parentkey.version",
            "title": "バージョン情報",
            "title_i18n": {
                "en": "Version Information",
                "ja": "バージョン情報"
            },
            "type": "text"
        },
        {
            "key": "parentkey.displaytype",
            "title": "表示形式",
            "titleMap": [
                {
                    "name": "詳細表示",
                    "name_i18n": {
                        "en": "Detail",
                        "ja": "詳細表示"
                    },
                    "value": "detail"
                },
                {
                    "name": "簡易表示",
                    "name_i18n": {
                        "en": "Simple",
                        "ja": "簡易表示"
                    },
                    "value": "simple"
                },
                {
                    "name": "プレビュー",
                    "name_i18n": {
                        "en": "Preview",
                        "ja": "プレビュー"
                    },
                    "value": "preview"
                }
            ],
            "title_i18n": {
                "en": "Preview",
                "ja": "表示形式"
            },
            "type": "select"
        },
        {
            "key": "parentkey.licensetype",
            "title": "ライセンス",
            "titleMap": [],
            "title_i18n": {
                "en": "License",
                "ja": "ライセンス"
            },
            "type": "select"
        },
        {
            "condition": "model.parentkey.licensetype == ''license_free''",
            "key": "parentkey[].licensefree",
            "title": " ",
            "type": "textarea"
        },
        {
            "default": "open_restricted",
            "key": "parentkey.accessrole",
            "title": "アクセス",
            "titleMap": [
                {
                    "name": "オープンアクセス",
                    "name_i18n": {
                        "en": "Open Access",
                        "ja": "オープンアクセス"
                    },
                    "value": "open_access"
                },
                {
                    "name": "オープンアクセス日を指定する",
                    "name_i18n": {
                        "en": "Input Open Access Date",
                        "ja": "オープンアクセス日を指定する"
                    },
                    "value": "open_date"
                },
                {
                    "name": "ログインユーザのみ",
                    "name_i18n": {
                        "en": "Registered User Only",
                        "ja": "ログインユーザのみ"
                    },
                    "value": "open_login"
                },
                {
                    "name": "公開しない",
                    "name_i18n": {
                        "en": "Do Not Publish",
                        "ja": "公開しない"
                    },
                    "value": "open_no"
                },
                {
                    "name": "制限公開",
                    "name_i18n": {
                        "en": "Limited Access",
                        "ja": "制限公開"
                    },
                    "value": "open_restricted"
                }
            ],
            "title_i18n": {
                "en": "Access",
                "ja": "アクセス"
            },
            "type": "radios"
        },
        {
            "condition": "model.parentkey[arrayIndex].accessrole == ''open_date''",
            "format": "yyyy-MM-dd",
            "key": "parentkey.accessdate",
            "templateUrl": "/static/templates/weko_deposit/datepicker.html",
            "title": "公開日",
            "type": "template"
        },
        {
            "add": "New",
            "condition": "model.parentkey[arrayIndex].accessrole == ''open_date'' || model.parentkey[arrayIndex].accessrole == ''open_login''",
            "items": [
                {
                    "key": "parentkey.roles[].role",
                    "title": "ロール",
                    "titleMap": [],
                    "type": "select"
                }
            ],
            "key": "parentkey.roles",
            "style": {
                "add": "btn-success"
            },
            "title": "ロール"
        },
        {
            "add": "New",
            "condition": "model.parentkey.accessrole == ''open_restricted''",
            "items": [
                {
                    "key": "parentkey.provide[].role",
                    "title": "ロール",
                    "titleMap": [],
                    "type": "select"
                },
                {
                    "key": "parentkey.provide[].workflow",
                    "title": "ワークフロー",
                    "titleMap": [],
                    "type": "select"
                }
            ],
            "key": "parentkey.provide",
            "style": {
                "add": "btn-success"
            },
            "title": "提供方法",
            "title_i18n": {
                "en": "Providing Method",
                "ja": "提供方法"
            }
        },
        {
            "condition": "model.parentkey.accessrole == ''open_restricted''",
            "key": "parentkey.terms",
            "title": "利用規約",
            "titleMap": [],
            "title_i18n": {
                "en": "Terms and Conditions",
                "ja": "利用規約"
            },
            "type": "select"
        },
        {
            "condition": "model.parentkey.accessrole == ''open_restricted'' && model.parentkey.terms== ''term_free''",
            "key": "parentkey.termsDescription",
            "title": " ",
            "type": "textarea"
        }
    ],
    "key": "parentkey",
    "title_i18n": {
        "en": "Restricted Access Content File",
        "ja": "制限公開用のコンテンツファイル"
    },
    "type": "fieldset"
}'::jsonb
WHERE id=30015;

UPDATE public.item_type_property
SET form = '
{
    "add": "New",
    "items": [
        {
            "key": "parentkey[].filename",
            "onChange": "fileNameSelect(this, form, modelValue)",
            "templateUrl": "/static/templates/weko_deposit/datalist.html",
            "title": "表示名",
            "titleMap": [],
            "title_i18n": {
                "en": "FileName",
                "ja": "表示名"
            },
            "type": "template"
        },
        {
            "items": [
                {
                    "disableSuccessState": true,
                    "feedback": false,
                    "fieldHtmlClass": "file-text-url",
                    "key": "parentkey[].url.url",
                    "title": "本文URL",
                    "title_i18n": {
                        "en": "Text URL",
                        "ja": "本文URL"
                    },
                    "type": "text"
                },
                {
                    "disableSuccessState": true,
                    "feedback": false,
                    "key": "parentkey[].url.label",
                    "title": "ラベル",
                    "title_i18n": {
                        "en": "Label",
                        "ja": "ラベル"
                    },
                    "type": "text"
                },
                {
                    "disableSuccessState": true,
                    "feedback": false,
                    "key": "parentkey[].url.objectType",
                    "title": "オブジェクトタイプ",
                    "titleMap": [
                        {
                            "name": "abstract",
                            "name_i18n": {
                                "en": "abstract",
                                "ja": "abstract"
                            },
                            "value": "abstract"
                        },
                        {
                            "name": "dataset",
                            "name_i18n": {
                                "en": "dataset",
                                "ja": "dataset"
                            },
                            "value": "dataset"
                        },
                        {
                            "name": "fulltext",
                            "name_i18n": {
                                "en": "fulltext",
                                "ja": "fulltext"
                            },
                            "value": "fulltext"
                        },
                        {
                            "name": "software",
                            "name_i18n": {
                                "en": "software",
                                "ja": "software"
                            },
                            "value": "software"
                        },
                        {
                            "name": "summary",
                            "name_i18n": {
                                "en": "summary",
                                "ja": "summary"
                            },
                            "value": "summary"
                        },
                        {
                            "name": "thumbnail",
                            "name_i18n": {
                                "en": "thumbnail",
                                "ja": "thumbnail"
                            },
                            "value": "thumbnail"
                        },
                        {
                            "name": "other",
                            "name_i18n": {
                                "en": "other",
                                "ja": "other"
                            },
                            "value": "other"
                        }
                    ],
                    "title_i18n": {
                        "en": "Object Type",
                        "ja": "オブジェクトタイプ"
                    },
                    "type": "select"
                }
            ],
            "key": "parentkey[].url",
            "title": "本文URL",
            "title_i18n": {
                "en": "Text URL",
                "ja": "本文URL"
            },
            "type": "fieldset"
        },
        {
            "key": "parentkey[].format",
            "title": "フォーマット",
            "title_i18n": {
                "en": "Format",
                "ja": "フォーマット"
            },
            "type": "text"
        },
        {
            "add": "New",
            "items": [
                {
                    "key": "parentkey[].filesize[].value",
                    "title": "サイズ",
                    "title_i18n": {
                        "en": "Size",
                        "ja": "サイズ"
                    },
                    "type": "text"
                }
            ],
            "key": "parentkey[].filesize",
            "style": {
                "add": "btn-success"
            },
            "title": "サイズ",
            "title_i18n": {
                "en": "Size",
                "ja": "サイズ"
            }
        },
        {
            "add": "New",
            "items": [
                {
                    "key": "parentkey[].fileDate[].fileDateType",
                    "title": "日付タイプ",
                    "titleMap": [
                        {
                            "name": "Accepted",
                            "value": "Accepted"
                        },
                        {
                            "name": "Collected",
                            "value": "Collected"
                        },
                        {
                            "name": "Copyrighted",
                            "value": "Copyrighted"
                        },
                        {
                            "name": "Issued",
                            "value": "Issued"
                        },
                        {
                            "name": "Submitted",
                            "value": "Submitted"
                        },
                        {
                            "name": "Updated",
                            "value": "Updated"
                        },
                        {
                            "name": "Valid",
                            "value": "Valid"
                        }
                    ],
                    "type": "select"
                },
                {
                    "format": "yyyy-MM-dd",
                    "key": "parentkey[].fileDate[].fileDateValue",
                    "templateUrl": "/static/templates/weko_deposit/datepicker.html",
                    "title": "日付",
                    "title_i18n": {
                        "en": "Date",
                        "ja": "日付"
                    },
                    "type": "template"
                }
            ],
            "key": "parentkey[].fileDate",
            "style": {
                "add": "btn-success"
            },
            "title": "日付",
            "title_i18n": {
                "en": "Date",
                "ja": "日付"
            }
        },
        {
            "key": "parentkey[].version",
            "title": "バージョン情報",
            "title_i18n": {
                "en": "Version Information",
                "ja": "バージョン情報"
            },
            "type": "text"
        },
        {
            "key": "parentkey[].displaytype",
            "title": "表示形式",
            "titleMap": [
                {
                    "name": "詳細表示",
                    "name_i18n": {
                        "en": "Detail",
                        "ja": "詳細表示"
                    },
                    "value": "detail"
                },
                {
                    "name": "簡易表示",
                    "name_i18n": {
                        "en": "Simple",
                        "ja": "簡易表示"
                    },
                    "value": "simple"
                },
                {
                    "name": "プレビュー",
                    "name_i18n": {
                        "en": "Preview",
                        "ja": "プレビュー"
                    },
                    "value": "preview"
                }
            ],
            "title_i18n": {
                "en": "Preview",
                "ja": "表示形式"
            },
            "type": "select"
        },
        {
            "key": "parentkey[].licensetype",
            "title": "ライセンス",
            "titleMap": [],
            "title_i18n": {
                "en": "License",
                "ja": "ライセンス"
            },
            "type": "select"
        },
        {
            "condition": "model.parentkey[arrayIndex].licensetype == ''license_free''",
            "key": "parentkey[].licensefree",
            "title": " ",
            "type": "textarea"
        },
        {
            "default": "open_restricted",
            "key": "parentkey[].accessrole",
            "title": "アクセス",
            "titleMap": [
                {
                    "name": "オープンアクセス",
                    "name_i18n": {
                        "en": "Open Access",
                        "ja": "オープンアクセス"
                    },
                    "value": "open_access"
                },
                {
                    "name": "オープンアクセス日を指定する",
                    "name_i18n": {
                        "en": "Input Open Access Date",
                        "ja": "オープンアクセス日を指定する"
                    },
                    "value": "open_date"
                },
                {
                    "name": "ログインユーザのみ",
                    "name_i18n": {
                        "en": "Registered User Only",
                        "ja": "ログインユーザのみ"
                    },
                    "value": "open_login"
                },
                {
                    "name": "公開しない",
                    "name_i18n": {
                        "en": "Do Not Publish",
                        "ja": "公開しない"
                    },
                    "value": "open_no"
                },
                {
                    "name": "制限公開",
                    "name_i18n": {
                        "en": "Limited Access",
                        "ja": "制限公開"
                    },
                    "value": "open_restricted"
                }
            ],
            "title_i18n": {
                "en": "Access",
                "ja": "アクセス"
            },
            "type": "radios"
        },
        {
            "condition": "model.parentkey[arrayIndex].accessrole == ''open_date''",
            "format": "yyyy-MM-dd",
            "key": "parentkey[].accessdate",
            "templateUrl": "/static/templates/weko_deposit/datepicker.html",
            "title": "公開日",
            "title_i18n": {
                "en": "Opendate",
                "ja": "公開日"
            },
            "type": "template"
        },
        {
            "add": "New",
            "condition": "model.parentkey[arrayIndex].accessrole == ''open_date'' || model.parentkey[arrayIndex].accessrole == ''open_login''",
            "items": [
                {
                    "key": "parentkey[].roles[].role",
                    "title": "ロール",
                    "titleMap": [],
                    "title_i18n": {
                        "en": "Role",
                        "ja": "ロール"
                    },
                    "type": "select"
                }
            ],
            "key": "parentkey[].roles",
            "style": {
                "add": "btn-success"
            },
            "title": "ロール",
            "titleMap": [],
            "title_i18n": {
                "en": "Role",
                "ja": "ロール"
            }
        },
        {
            "add": "New",
            "condition": "model.parentkey[arrayIndex].accessrole == ''open_restricted''",
            "items": [
                {
                    "key": "parentkey[].provide[].workflow",
                    "title": "ワークフロー",
                    "titleMap": [],
                    "title_i18n": {
                        "en": "WorkFlow",
                        "ja": "ワークフロー"
                    },
                    "type": "select"
                },
                {
                    "key": "parentkey[].provide[].role",
                    "title": "ロール",
                    "titleMap": [],
                    "title_i18n": {
                        "en": "Role",
                        "ja": "ロール"
                    },
                    "type": "select"
                }
            ],
            "key": "parentkey[].provide",
            "style": {
                "add": "btn-success"
            },
            "title": "提供方法",
            "title_i18n": {
                "en": "Providing Method",
                "ja": "提供方法"
            }
        },
        {
            "condition": "model.parentkey[arrayIndex].accessrole == ''open_restricted''",
            "key": "parentkey[].terms",
            "title": "利用規約",
            "titleMap": [],
            "title_i18n": {
                "en": "Terms and Conditions",
                "ja": "利用規約"
            },
            "type": "select"
        },
        {
            "condition": "model.parentkey[arrayIndex].accessrole == ''open_restricted'' && model.parentkey[arrayIndex].terms== ''term_free''",
            "key": "parentkey[].termsDescription",
            "title": " ",
            "type": "textarea"
        }
    ],
    "key": "parentkey",
    "style": {
        "add": "btn-success"
    },
    "title_i18n": {
        "en": "Restricted Access Content File",
        "ja": "制限公開用のコンテンツファイル"
    }
}
'::jsonb
WHERE id=30015;