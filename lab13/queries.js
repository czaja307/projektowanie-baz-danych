db.donors.aggregate([
  {
    $group: {
      _id: {
        blood_type: "$blood_type",
        blood_rh: "$blod_rh"
      },
      donor_count: {$sum: 1}
    }
  },
  {
    $project: {
      _id: 0,
      blood_group: {
        $concat: ["$_id.blood_type", "$_id.blood_rh"]
      },
      donor_count: 1
    }
  },
  {
    $sort: {donor_count: 1}
  }
]);


db.blood_bags.aggregate([
  {

    $match: {
      "lab_result.is_qualified": true,
      order: {$exists: false}
    }
  },
  {

    $lookup: {
      from: "donors",
      localField: "donation.donor_id",
      foreignField: "_id",
      as: "donor"
    }
  },

  {$unwind: "$donor"},
  {
    $group: {
      _id: {
        blood_type: "$donor.blood_type",
        blood_rh: "$donor.blod_rh"
      },
      available_bags: {$sum: 1}
    }
  },
  {
    $project: {
      _id: 0,
      blood_group: {$concat: ["$_id.blood_type", "$_id.blood_rh"]},
      available_bags: 1
    }
  },
  {
    $sort: {available_bags: 1}
  }
]);


db.orders.aggregate([
  {$unwind: "$realizations"},

  {
    $group: {
      _id: "$realizations.transport.driver_id",
      realizations_count: {$sum: 1}
    }
  },

  {
    $lookup: {
      from: "drivers",
      localField: "_id",
      foreignField: "_id",
      as: "driver_info"
    }
  },

  {$unwind: "$driver_info"},

  {
    $project: {
      driver_id: "$_id",
      name: "$driver_info.name",
      last_name: "$driver_info.last_name",
      realizations_count: 1
    }
  },

  {$sort: {realizations_count: -1}}

])


db.blood_bags.aggregate([

  {
    $group: {
      _id: "$donation.donor_id",
      donation_count: {$sum: 1}
    }
  },

  {
    $lookup: {
      from: "donors",
      localField: "_id",
      foreignField: "_id",
      as: "donor"
    }
  },
  {$unwind: "$donor"},


  {
    $project: {
      donor_id: "$_id",
      donor_name: "$donor.name",
      donor_last_name: "$donor.last_name",
      donor_pesel: "$donor.pesel",
      donation_count: 1
    }
  },
  {$sort: {donation_count: -1}}
]);


db.donors.aggregate([
  {$unwind: "$examinations"},
  {
    $group: {
      _id: null,
      total_exams: {$sum: 1},
      disqualified_count: {
        $sum: {
          $cond: [
            {$eq: ["$examinations.is_qualified", false]},
            1,
            0
          ]
        }
      }
    }
  },
  {
    $project: {
      disqualified_percentage: {
        $multiply: [
          {$divide: ["$disqualified_count", "$total_exams"]},
          100
        ]
      }
    }
  }
]);


db.blood_bags.aggregate([
  {
    $group: {
      _id: "$donation.donor_id",
      last_donation_date: {$max: "$donation.date"}
    }
  },
  {
    $match: {
      last_donation_date: {$lte: new Date(new Date().setMonth(new Date().getMonth() - 1))}
    }
  },
  {
    $lookup: {
      from: "donors",
      localField: "_id",
      foreignField: "_id",
      as: "donor_info"
    }
  },
  {$unwind: "$donor_info"},
  {
    $project: {
      donor_id: "$_id",
      name: "$donor_info.name",
      last_name: "$donor_info.last_name",
      pesel: "$donor_info.pesel",
      last_donation_date: 1
    }
  },
  {
    $sort: {last_donation_date: 1}
  }
]);


db.orders.find(
  {
    state: "awaiting",
    is_urgent: true
  },
);


db.blood_bags.aggregate([
  {
    $match: {
      "donation.date": {
        $gte: new Date(new Date().getTime() - 365 * 24 * 60 * 60 * 1000)
      }
    }
  },
  {
    $group: {
      _id: "$donation.donor_id",
      donation_count: {$sum: 1}
    }
  },
  {
    $match: {
      donation_count: {$gte: 5}
    }
  },
  {
    $lookup: {
      from: "donors",
      localField: "_id",
      foreignField: "_id",
      as: "donor"
    }
  },
  {$unwind: "$donor"},
  {
    $project: {
      _id: 0,
      donor_id: "$_id",
      first_name: "$donor.first_name",
      last_name: "$donor.last_name",
      donation_count: 1
    }
  },
  {
    $sort: {donation_count: -1}
  }
]);


db.donors.aggregate([
  {$unwind: "$examinations"},
  {
    $group: {
      _id: null,
      avg_weight: {$avg: "$examinations.weight"},
      avg_height: {$avg: "$examinations.height"}
    }
  },
  {
    $project: {
      _id: 0,
      avg_weight: 1,
      avg_height: 1
    }
  }
]);


db.blood_bags.aggregate([
  {

    $match: {
      "lab_result.is_qualified": {$exists: true}

    }
  },

  {
    $lookup: {
      from: "donors",
      localField: "donation.donor_id",
      foreignField: "_id",
      as: "donor"
    }
  },
  {$unwind: "$donor"},

  {
    $group: {
      _id: {
        blood_type: "$donor.blood_type",
        blod_rh: "$donor.blod_rh"
      },

      avg_hemoglobin: {$avg: "$lab_result.hemoglobin_level"},
      avg_red_cells: {$avg: "$lab_result.red_cells_count"},

    }
  },
  {
    $project: {
      _id: 0,
      blood_group: {
        $concat: ["$_id.blood_type", "$_id.blod_rh"]
      },
      avg_hemoglobin: 1,
      avg_red_cells: 1
    }
  }
]);


db.donors.aggregate([

  {$unwind: "$examinations"},
  {

    $match: {
      "examinations.date": {
        $gte: new Date("2024-01-01T00:00:00Z"),
        $lt: new Date("2025-01-01T00:00:00Z")
      }
    }
  },
  {
    $group: {
      _id: "$examinations.doctor_id",
      examination_count: {$sum: 1}
    }
  },

  {
    $lookup: {
      from: "doctors",
      localField: "_id",
      foreignField: "_id",
      as: "doctor_info"
    }
  },
  {$unwind: "$doctor_info"},

  {
    $project: {
      doctor_id: "$_id",
      name: "$doctor_info.name",
      last_name: "$doctor_info.last_name",

      examination_count: 1
    }
  },
  {$sort: {examination_count: -1}}
]);


db.blood_bags.aggregate([
  {
    $group: {
      _id: "$facility_id",
      total_donations: {$sum: 1},
      qualified_donations: {
        $sum: {
          $cond: [
            {$eq: ["$lab_result.is_qualified", true]},
            1,
            0
          ]
        }
      },
      available_bags: {
        $sum: {
          $cond: [
            {
              $and: [
                {$eq: ["$lab_result.is_qualified", true]},
                {$not: [{$ifNull: ["$order", false]}]}
              ]
            },
            1,
            0
          ]
        }
      }
    }
  },

  {
    $lookup: {
      from: "facilities",
      localField: "_id",
      foreignField: "_id",
      as: "facility"
    }
  },
  {$unwind: "$facility"},
  {
    $project: {
      _id: 0,
      facility_id: "$facility._id",
      facility_name: "$facility.name",
      total_donations: 1,
      qualified_donations: 1,
      available_blood_bags: "$available_bags"
    }
  },
  {
    $sort: {available_blood_bags: -1}
  }
]);


db.blood_bags.aggregate([
  {

    $match: {
      "lab_result.date": {$exists: true},
      "donation.date": {$exists: true}
    }
  },
  {
    $group: {
      _id: "$facility_id",
      avg_qualification_time: {

        $avg: {
          $divide: [
            {$subtract: ["$lab_result.date", "$donation.date"]},
            3600000
          ]
        }
      }
    }
  },

  {
    $lookup: {
      from: "facilities",
      localField: "_id",
      foreignField: "_id",
      as: "facility"
    }
  },
  {$unwind: "$facility"},
  {
    $project: {
      facility_id: "$facility._id",
      facility_name: "$facility.name",

      avg_qualification_time_in_hours: "$avg_qualification_time"
    }
  },
  {$sort: {avg_qualification_time_in_hours: 1}}
]);


db.donors.aggregate([

  {$unwind: "$certificates"},

  {
    $lookup: {
      from: "blood_bags",
      localField: "_id",
      foreignField: "donation.donor_id",
      as: "bags"
    }
  },
  {
    $project: {
      donor_id: "$_id",
      name: "$name",
      last_name: "$last_name",
      "certificates.level": 1,
      "certificates.acquisitiion_date": 1,

      donated_blood_ml: {
        $sum: "$bags.volume"
      }
    }
  },
  {
    $sort: {"certificates.level": 1}
  }
]);


db.blood_bags.aggregate([
  {
    $group: {
      _id: "$donation.donor_id",
      donation_count: {$sum: 1}
    }
  },
  {


    $group: {
      _id: null,
      avg_donations_per_donor: {$avg: "$donation_count"}
    }
  },
  {
    $project: {
      _id: 0,
      avg_donations_per_donor: 1
    }
  }
]);


db.orders.aggregate([
  {
    $group: {
      _id: "$hospital.hospital_id",
      order_count: {$sum: 1}
    }
  },
  {
    $lookup: {
      from: "hospitals",
      localField: "_id",
      foreignField: "_id",
      as: "hospital_doc"
    }
  },
  {$unwind: "$hospital_doc"},
  {
    $project: {
      hospital_id: "$_id",
      name: "$hospital_doc.name",
      order_count: 1
    }
  },
  {$sort: {order_count: -1}}
]);