// Copyright (c) 2021, Greycube and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Man Visit", {
  setup: function (frm) {
    frm.set_query("visit_to", function () {
      return {
        filters: {
          name: ["in", ["Customer", "Lead"]],
        },
      };
    });
  },

  visit_to: function (frm) {
    frm.set_value("party", "");
  },

  party: function (frm) {
    if (frm.doc.visit_to == "Customer") {
      frappe.call({
        method:
          "almofa.almofa.doctype.sales_man_visit.sales_man_visit.get_client_location",
        args: { party: frm.doc.party },
        callback: (r) => {
          frm.set_value("client_location", r.message);
        },
      });
    } else {
      frm.set_value("client_location", "");
    }
  },

  setup_opportunity_from: function (frm) {
    frm.trigger("setup_queries");
    frm.trigger("set_dynamic_field_label");
  },

  validate: function (frm) {
    if (!frm.doc.visit_to == "Customer") {
      return true;
    }
    return new Promise((resolve, reject) => {
      get_user_location().then((user_loc) => {
        let client_loc = frm.doc.client_location
          .split(",")
          .map((r) => parseFloat(r));

        let distance = haversineDistance(client_loc, user_loc) * 1000;
        if (distance < 250) {
          resolve();
        } else {
          frappe.throw(
            `User location error. User is ${distance.toFixed()}m away from client's location.`
          );
          reject();
        }
      });
    });
  },
});

async function get_user_location() {
  return new Promise((resolve, reject) => {
    // check geolocation api is available
    if (!navigator.geolocation) {
      frappe.throw(__("Geolocation is not enabled."));
      reject();
    }

    // return client location for local test. Uncomment in production
    resolve(
      cur_frm.doc.client_location.split(",").map((r) => parseFloat(r) - 1.001)
    );
    return;
    //
    navigator.geolocation.getCurrentPosition(
      (loc) => {
        resolve([loc.coords.latitude, loc.coords.longitude]);
      },
      (err) => {
        frappe.throw(err.message);
        reject([]);
      }
    );
  });
}

const haversineDistance = ([lat1, lon1], [lat2, lon2], isMiles = false) => {
  const toRadian = (angle) => (Math.PI / 180) * angle;
  const distance = (a, b) => (Math.PI / 180) * (a - b);
  const RADIUS_OF_EARTH_IN_KM = 6371;

  const dLat = distance(lat2, lat1);
  const dLon = distance(lon2, lon1);

  lat1 = toRadian(lat1);
  lat2 = toRadian(lat2);

  // Haversine Formula
  const a =
    Math.pow(Math.sin(dLat / 2), 2) +
    Math.pow(Math.sin(dLon / 2), 2) * Math.cos(lat1) * Math.cos(lat2);
  const c = 2 * Math.asin(Math.sqrt(a));

  let finalDistance = RADIUS_OF_EARTH_IN_KM * c;

  if (isMiles) {
    finalDistance /= 1.60934;
  }

  console.log("Distance to client location is ", finalDistance);
  return finalDistance;
};
