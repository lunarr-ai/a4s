'use strict';
const MANIFEST = 'flutter-app-manifest';
const TEMP = 'flutter-temp-cache';
const CACHE_NAME = 'flutter-app-cache';

const RESOURCES = {"assets/AssetManifest.bin": "bcdcd6ad4049cd94140e922e1f3fbeff",
"assets/AssetManifest.bin.json": "3fb520b864fb30c37a21dbe412707b4e",
"assets/assets/avatars/1.png": "f30cca194d1ee701daedec7582bf2891",
"assets/assets/avatars/10.png": "0b36711691cd0b5a2c6a3e240cd2d09c",
"assets/assets/avatars/11.png": "9040a421f78574e8c7777b2b12aba890",
"assets/assets/avatars/12.png": "763b99488ab0a9dba7bb226fde171247",
"assets/assets/avatars/13.png": "c30669a10acfa7198a15911ba463d4b8",
"assets/assets/avatars/14.png": "6acc41436713c1a9577f4df4ff664782",
"assets/assets/avatars/15.png": "75bfe7235aae9d8ab88a19898d450269",
"assets/assets/avatars/16.png": "e3d631d7d2add8b007176c0414cce1b1",
"assets/assets/avatars/17.png": "2149ac2d1da01832721c2d3d5441887f",
"assets/assets/avatars/18.png": "0698a568c495bf55e2c082d661bfa44b",
"assets/assets/avatars/19.png": "5d1cea7f4f101dc0939ac06936c8987d",
"assets/assets/avatars/2.png": "bf5408845c984b2753d0f560aa26743c",
"assets/assets/avatars/20.png": "48f845626a812a448e44323c38e4de64",
"assets/assets/avatars/21.png": "6502d61d82e7b509e18a98f2c4e28e6e",
"assets/assets/avatars/22.png": "348b22dfc148994f1802c438ea32978b",
"assets/assets/avatars/23.png": "7671c7c5b98a312eb913c3033b52d7e5",
"assets/assets/avatars/24.png": "587a0bbb4139304603f30bff1f9966b0",
"assets/assets/avatars/25.png": "12996a4996dec41b05c27eb61eb2efa7",
"assets/assets/avatars/26.png": "4a95b3dcc0a414b586113ceea1427b06",
"assets/assets/avatars/27.png": "a26f2a5fe69b4d7c16cdc96ef5afe8e2",
"assets/assets/avatars/28.png": "6639e02d8ae59c2d253a3277d928e008",
"assets/assets/avatars/29.png": "8643be984266cec6bd989a1b6c0afa6f",
"assets/assets/avatars/3.png": "bb895c7f7082829127597b396df78c20",
"assets/assets/avatars/30.png": "4d924089184b38fced85f1b4ca329713",
"assets/assets/avatars/4.png": "9dfca08def477421121ff5d05221ab29",
"assets/assets/avatars/5.png": "c0241a6f64c76c3951025c8d4f0581cf",
"assets/assets/avatars/6.png": "63d87a05d79516435f68f904ca3cffa6",
"assets/assets/avatars/7.png": "81d107564662ecc5d22c84d5fba730b4",
"assets/assets/avatars/8.png": "5f040b2b07374b266cff7e344f26deb5",
"assets/assets/avatars/9.png": "a2e4fc98ffffb53fe561e9705cdbd3fb",
"assets/assets/fonts/GoogleSans-Italic.ttf": "8db7113e37a6cb5ab1d6ca620dd7081d",
"assets/assets/fonts/GoogleSans.ttf": "c98a147e31d33b276dbfced370e1348d",
"assets/assets/fonts/Roboto-Italic.ttf": "5b03341126c5c0b1d4db52bca7f45599",
"assets/assets/fonts/Roboto.ttf": "3aa911d4a1e76c8946952fe744ce7434",
"assets/assets/images/logo.png": "01435d546255fe1bb3259bc4e38e1808",
"assets/FontManifest.json": "7f299355850c429d83e2de2988971a32",
"assets/fonts/MaterialIcons-Regular.otf": "8166599cdbc98a6eb398f255bb3bc715",
"assets/NOTICES": "32a12292acbdaf4ed426aea28c8cb8ba",
"assets/packages/cupertino_icons/assets/CupertinoIcons.ttf": "33b7d9392238c04c131b6ce224e13711",
"assets/shaders/ink_sparkle.frag": "ecc85a2e95f5e9f53123dcaf8cb9b6ce",
"assets/shaders/stretch_effect.frag": "40d68efbbf360632f614c731219e95f0",
"canvaskit/canvaskit.js": "8331fe38e66b3a898c4f37648aaf7ee2",
"canvaskit/canvaskit.js.symbols": "a3c9f77715b642d0437d9c275caba91e",
"canvaskit/canvaskit.wasm": "9b6a7830bf26959b200594729d73538e",
"canvaskit/chromium/canvaskit.js": "a80c765aaa8af8645c9fb1aae53f9abf",
"canvaskit/chromium/canvaskit.js.symbols": "e2d09f0e434bc118bf67dae526737d07",
"canvaskit/chromium/canvaskit.wasm": "a726e3f75a84fcdf495a15817c63a35d",
"canvaskit/skwasm.js": "8060d46e9a4901ca9991edd3a26be4f0",
"canvaskit/skwasm.js.symbols": "3a4aadf4e8141f284bd524976b1d6bdc",
"canvaskit/skwasm.wasm": "7e5f3afdd3b0747a1fd4517cea239898",
"canvaskit/skwasm_heavy.js": "740d43a6b8240ef9e23eed8c48840da4",
"canvaskit/skwasm_heavy.js.symbols": "0755b4fb399918388d71b59ad390b055",
"canvaskit/skwasm_heavy.wasm": "b0be7910760d205ea4e011458df6ee01",
"favicon.png": "01435d546255fe1bb3259bc4e38e1808",
"flutter.js": "24bc71911b75b5f8135c949e27a2984e",
"flutter_bootstrap.js": "2347ad70df7fbd611fe08ce4b9a3104c",
"icons/Icon-192.png": "ac9a721a12bbc803b44f645561ecb1e1",
"icons/Icon-512.png": "96e752610906ba2a93c65f8abe1645f1",
"icons/Icon-maskable-192.png": "c457ef57daa1d16f64b27b786ec2ea3c",
"icons/Icon-maskable-512.png": "301a7604d45b3e739efc881eb04896ea",
"index.html": "f6482f8a3fcda3037d4c0e2258b43691",
"/": "f6482f8a3fcda3037d4c0e2258b43691",
"main.dart.js": "e141dc47becd2fcc3f0bcf89088e6cc3",
"manifest.json": "89bfc7df835edfae54ce030ffca6597e",
"version.json": "3afdb5470645554d2bff0d1f319a5faa"};
// The application shell files that are downloaded before a service worker can
// start.
const CORE = ["main.dart.js",
"index.html",
"flutter_bootstrap.js",
"assets/AssetManifest.bin.json",
"assets/FontManifest.json"];

// During install, the TEMP cache is populated with the application shell files.
self.addEventListener("install", (event) => {
  self.skipWaiting();
  return event.waitUntil(
    caches.open(TEMP).then((cache) => {
      return cache.addAll(
        CORE.map((value) => new Request(value, {'cache': 'reload'})));
    })
  );
});
// During activate, the cache is populated with the temp files downloaded in
// install. If this service worker is upgrading from one with a saved
// MANIFEST, then use this to retain unchanged resource files.
self.addEventListener("activate", function(event) {
  return event.waitUntil(async function() {
    try {
      var contentCache = await caches.open(CACHE_NAME);
      var tempCache = await caches.open(TEMP);
      var manifestCache = await caches.open(MANIFEST);
      var manifest = await manifestCache.match('manifest');
      // When there is no prior manifest, clear the entire cache.
      if (!manifest) {
        await caches.delete(CACHE_NAME);
        contentCache = await caches.open(CACHE_NAME);
        for (var request of await tempCache.keys()) {
          var response = await tempCache.match(request);
          await contentCache.put(request, response);
        }
        await caches.delete(TEMP);
        // Save the manifest to make future upgrades efficient.
        await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
        // Claim client to enable caching on first launch
        self.clients.claim();
        return;
      }
      var oldManifest = await manifest.json();
      var origin = self.location.origin;
      for (var request of await contentCache.keys()) {
        var key = request.url.substring(origin.length + 1);
        if (key == "") {
          key = "/";
        }
        // If a resource from the old manifest is not in the new cache, or if
        // the MD5 sum has changed, delete it. Otherwise the resource is left
        // in the cache and can be reused by the new service worker.
        if (!RESOURCES[key] || RESOURCES[key] != oldManifest[key]) {
          await contentCache.delete(request);
        }
      }
      // Populate the cache with the app shell TEMP files, potentially overwriting
      // cache files preserved above.
      for (var request of await tempCache.keys()) {
        var response = await tempCache.match(request);
        await contentCache.put(request, response);
      }
      await caches.delete(TEMP);
      // Save the manifest to make future upgrades efficient.
      await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
      // Claim client to enable caching on first launch
      self.clients.claim();
      return;
    } catch (err) {
      // On an unhandled exception the state of the cache cannot be guaranteed.
      console.error('Failed to upgrade service worker: ' + err);
      await caches.delete(CACHE_NAME);
      await caches.delete(TEMP);
      await caches.delete(MANIFEST);
    }
  }());
});
// The fetch handler redirects requests for RESOURCE files to the service
// worker cache.
self.addEventListener("fetch", (event) => {
  if (event.request.method !== 'GET') {
    return;
  }
  var origin = self.location.origin;
  var key = event.request.url.substring(origin.length + 1);
  // Redirect URLs to the index.html
  if (key.indexOf('?v=') != -1) {
    key = key.split('?v=')[0];
  }
  if (event.request.url == origin || event.request.url.startsWith(origin + '/#') || key == '') {
    key = '/';
  }
  // If the URL is not the RESOURCE list then return to signal that the
  // browser should take over.
  if (!RESOURCES[key]) {
    return;
  }
  // If the URL is the index.html, perform an online-first request.
  if (key == '/') {
    return onlineFirst(event);
  }
  event.respondWith(caches.open(CACHE_NAME)
    .then((cache) =>  {
      return cache.match(event.request).then((response) => {
        // Either respond with the cached resource, or perform a fetch and
        // lazily populate the cache only if the resource was successfully fetched.
        return response || fetch(event.request).then((response) => {
          if (response && Boolean(response.ok)) {
            cache.put(event.request, response.clone());
          }
          return response;
        });
      })
    })
  );
});
self.addEventListener('message', (event) => {
  // SkipWaiting can be used to immediately activate a waiting service worker.
  // This will also require a page refresh triggered by the main worker.
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
    return;
  }
  if (event.data === 'downloadOffline') {
    downloadOffline();
    return;
  }
});
// Download offline will check the RESOURCES for all files not in the cache
// and populate them.
async function downloadOffline() {
  var resources = [];
  var contentCache = await caches.open(CACHE_NAME);
  var currentContent = {};
  for (var request of await contentCache.keys()) {
    var key = request.url.substring(origin.length + 1);
    if (key == "") {
      key = "/";
    }
    currentContent[key] = true;
  }
  for (var resourceKey of Object.keys(RESOURCES)) {
    if (!currentContent[resourceKey]) {
      resources.push(resourceKey);
    }
  }
  return contentCache.addAll(resources);
}
// Attempt to download the resource online before falling back to
// the offline cache.
function onlineFirst(event) {
  return event.respondWith(
    fetch(event.request).then((response) => {
      return caches.open(CACHE_NAME).then((cache) => {
        cache.put(event.request, response.clone());
        return response;
      });
    }).catch((error) => {
      return caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((response) => {
          if (response != null) {
            return response;
          }
          throw error;
        });
      });
    })
  );
}
