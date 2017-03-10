/*global require*/
'use strict';

// Require.js allows us to configure shortcut alias
require.config({
	// The shim config allows us to configure dependencies for
	// scripts that do not call define() to register a module
	shim: {
		underscore: {
			exports: '_'
		},
		backbone: {
			deps: [
				'underscore',
				'jquery'
			],
			exports: 'Backbone'
		},
		backboneLocalstorage: {
			deps: ['backbone'],
			exports: 'Store'
		}
	},
	paths: {
		jquery: 'modules/jquery/jquery',
		underscore: 'modules/underscore/underscore',
		backbone: 'modules/backbone/backbone',
		backboneLocalstorage: 'modules/backbone.localstorage/backbone.localStorage',
		text: 'modules/requirejs-text/text'
	}
});

require([
	'backbone',
	'views/app',
	'routers/router'
], function (Backbone, AppView, Workspace) {
	/*jshint nonew:false*/
	// Initialize routing and start Backbone.history()
	new Workspace();
	Backbone.history.start();

	// Initialize the application view
	new AppView();
});
