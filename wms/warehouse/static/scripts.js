function getCSRFToken() {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          let cookie = cookies[i].trim();
          if (cookie.substring(0, 'csrftoken='.length) === 'csrftoken=') {
              cookieValue = decodeURIComponent(cookie.substring('csrftoken='.length));
              break;
          }
      }
  }
  return cookieValue;
}

$.ajaxSetup({
  beforeSend: function(xhr, settings) {
      if (!this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
      }
  }
});

var table;

$(document).ready(function(){
  table = $('#table').DataTable({
    "processing": true,
    "serverSide": true,
    "ajax": {
        "url": "",
        "type": "GET"
    },
    "dom": 'Bflrtip',
    "buttons": [
        {
            extend: 'excel',
            exportOptions: {
                columns: ':not(:nth-last-child(-n+2))' // Exclude the last two columns
            }
        },
        {
            extend: 'pdf',
            exportOptions: {
                columns: ':not(:nth-last-child(-n+2))' // Exclude the last two columns
            }
        },
        'colvis'
    ],
    "columns": [
        { "data": "productId" },
        { "data": "company" },
        { "data": "stockType" },
        { "data": "quantity" },
        { "data": "location" },
        { "data": null,
            "render": function(data, type, row) {
                return '<div class="dropdown">' +
                       '<button class="btn btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">Manage</button>' +
                       '<ul class="dropdown-menu">' +
                       '<li><a class="dropdown-item" href="/viewIndvChangesStock?id=' + row.id + '">View Stock Changes</a></li>' +
                       '<li><a class="dropdown-item" href="/viewServiceHistoryStock?id=' + row.id + '">View Service History</a></li>' +
                       '<li><a class="dropdown-item" href="javascript:void(0);" onclick="openLocationModal(\'' + row.location + '\', ' + row.id + ')">Change Location</a></li>'+
                       (row.stockType == 'SK' ? '<li><a class="dropdown-item" href="javascript:void(0);" onclick="openAdjustModal(' + row.id + ')">Adjustment</a></li>' : '') +
                       '<li><a class="dropdown-item" href="/dispatchStock?id=' + row.id + '">Dispatch</a></li>' +
                       '<li><a class="dropdown-item" href="javascript:void(0);" onclick="openDeleteModal(' + row.id + ')">Delete</a></li>' +
                       '</ul></div>';
            },
            "orderable": false,
            "searchable": false },
        { "data": null,
            "render": function(data, type, row) {
                return '<div class="dropdown">' +
                       '<button class="btn btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">Service</button>' +
                       '<ul class="dropdown-menu">' +
                       (row.stockType == 'SK' ? '<li><a class="dropdown-item" href="javascript:void(0);" onclick="openChangeLabelModal(\'' + row.productId + '\', ' + row.id + ')">Change Label</a></li>' : '') +
                       '<li><a class="dropdown-item" href="javascript:void(0);" onclick="openAssortingModal(\'' + row.productId + '\', ' + row.id + ')">Assorting</a></li>' +
                       (row.stockType == 'SK' ? '<li><a class="dropdown-item" href="javascript:void(0);" onclick="openChangeCardModal(\'' + row.productId + '\', ' + row.id + ')">Change Card</a></li>' : '') +
                       '<li><a class="dropdown-item" href="javascript:void(0);" onclick="openClearanceModal(\'' + row.productId + '\', ' + row.id + ')">Clearance</a></li>' +
                       '<li><a class="dropdown-item" href="javascript:void(0);" onclick="openDestroyModal(\'' + row.productId + '\', ' + row.id + ')">Destroy</a></li>' +
                       (row.stockType == 'CA' ? '<li><a class="dropdown-item" href="javascript:void(0);" onclick="openInspectionModal(\'' + row.productId + '\', ' + row.id + ')">Inspection</a></li>' : '') +
                       '<li><a class="dropdown-item" href="javascript:void(0);" onclick="openPhotoModal(\'' + row.productId + '\', ' + row.id + ')">Photo</a></li>' +
                       '</ul></div>';
            },
            "orderable": false, 
            "searchable": false }
    ]});
  table.buttons().container()
        .appendTo( '#example_wrapper .col-md-6:eq(0)' );
});


function openLocationModal(location, id) {
    var modalHtml = `
        <div class="modal fade" id='changeLoc' tabindex="-1" aria-labelledby="AdjustStock" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h1 class="modal-title fs-5" id="AdjustStock">Internal Adjustment</h1>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                Current Location: <b>${location}</b> <br>
                Please enter the new location:
                <input class = 'form-control' type = 'text' placeholder = 'Location' name = 'location'/>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary" id="submitChange">Submit</button>
              </div>
            </div>
          </div>
        </div>
    `;

    // Append the modal to the body
    $('body').append(modalHtml);

    // Show the modal
    $('#changeLoc').modal('show');

    // Attach event listener to the submit button within the modal
    $('#submitChange').on('click', function() {
      // Capture the form data
      var newLocation = $('input[name="location"]').val();
      
      // AJAX request
      $.ajax({
          url: '/changeLocation',
          type: 'POST',
          data: {
              id: id,
              location: newLocation,
              csrfmiddlewaretoken: getCSRFToken()
          },
          success: function(response) {
              // Handle success
              $('#changeLoc').modal('hide');
              $('#changeLoc').remove();
              table.ajax.reload(null, false);
          },
          error: function(xhr, status, error) {
              // Handle error
              console.error("Error: " + error);
          }
      });
  });

    // Remove the modal from the DOM when it's closed to avoid duplicate IDs
    $('#changeLoc').on('hidden.bs.modal', function () {
        $(this).remove();
    });
}

function openAdjustModal(id) {
    var modalHtml = `
      <div class="modal fade" id='adjustModal' tabindex="-1" aria-labelledby="AdjustStock" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5" id="AdjustStock">Internal Adjustment</h1>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              
              <div class="form-check">
                <input class="form-check-input" type="radio" name="incOrDec" id="flexRadioDefault1" value="increase" checked>
                <label class="form-check-label" for="flexRadioDefault1">
                  Increase Stock
                </label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="radio" name="incOrDec" id="flexRadioDefault2" value="decrease">
                <label class="form-check-label" for="flexRadioDefault2">
                  Decrease Stock
                </label>
              </div>

              How much would you like to adjust by?
              <input class='form-control' type='number' placeholder='Quantity' name='quantity' min="1"/>
          
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <button type="button" class="btn btn-primary" id="submitChange">Submit</button>
            </div>
          </div>
        </div>
      </div>
    `;

    // Append the modal to the body
    $('body').append(modalHtml);

    // Show the modal
    $('#adjustModal').modal('show');

    // Attach event listener to the submit button within the modal
    $('#submitChange').on('click', function() {
      // Capture the form data
      var incOrDec = $('input[name="incOrDec"]:checked').val();
      var quantity = $('input[name="quantity"]').val();
      
      // AJAX request
      $.ajax({
        url: '/adjustStock',
        type: 'POST',
        data: {
            id: id,
            incOrDec: incOrDec,
            quantity: quantity,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
          // Handle success
          $('#adjustModal').modal('hide');
          $('#adjustModal').remove();
          // Refresh the page
          table.ajax.reload(null, false);
          $('#messageContainer').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
        },
        error: function(xhr, status, error) {
          // Handle error
          console.error("Error: " + error);
          $('#messageContainer').html('<div class="alert alert-danger" role="alert">' + response.message + '</div>');
        }
      });
    });

    // Remove the modal from the DOM when it's closed to avoid duplicate IDs
    $('#adjustModal').on('hidden.bs.modal', function () {
      $(this).remove();
    });
}

function openDeleteModal(id) {
    var modalHtml = `
      <div class="modal fade" id='deleteModal' tabindex="-1" aria-labelledby="DeleteCheck" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="DeleteCheck">Delete</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to delete this stock entry?
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <a href="/deleteStock?id=`+ id +`"><button type="button" class="btn btn-primary">Delete</button></a>
          </div>
        </div>
      </div>
    </div>
    `;

    // Append the modal to the body
    $('body').append(modalHtml);

    // Show the modal
    $('#deleteModal').modal('show');

    // Remove the modal from the DOM when it's closed to avoid duplicate IDs
    $('#deleteModal').on('hidden.bs.modal', function () {
        $(this).remove();
    });
}

function openChangeLabelModal(productId, id) {
    var modalHtml = `
      <div class="modal fade" id='changeLabelModal' tabindex="-1" aria-labelledby="changeLabelModal" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5" id="changeLabelModal">Change Label</h1>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              You are changing label for <b>` + productId + `</b>
              <br>
              <input class="form-control"  type="text" name="label" placeholder="New Label ID" >
              <br>
              <input class="form-control"  type="number" name="number" placeholder="Number of SKUs to Change" >
              <br>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <button type="submit" class="btn btn-primary" id="submitChange">Submit</button>
            </div>
          </div>
        </div>
      </div>
    `;

    // Append the modal to the body
    $('body').append(modalHtml);

    // Show the modal
    $('#changeLabelModal').modal('show');

    $('#submitChange').on('click', function() {
      var label = $('input[name="label"]').val();
      var number = $('input[name="number"]').val();

      $.ajax({
        url: '/labelChange',
        type: 'POST',
        data: {
            id: id,
            label: label,
            number: number,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
          $('#changeLabelModal').modal('hide');
          $('#changeLabelModal').remove();
          table.ajax.reload(null, false);
          $('#messageContainer').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
        },
        error: function(xhr, status, error) {
          console.error("Error: " + error);
          $('#messageContainer').html('<div class="alert alert-danger" role="alert">' + response.message + '</div>');
        }
      });
    });

    $('#changeLabelModal').on('hidden.bs.modal', function () {
      $(this).remove();
    });
}

function openAssortingModal(productId, id) {
    var modalHtml = `
      <div class="modal fade" id='assortingModal' tabindex="-1" aria-labelledby="assortingModal" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="assortingModal">Assorting</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          You are assorting for <b>` + productId + `</b>
          <br>
          <input class="form-control" type="number" placeholder="Enter Number of SKU to add" name="skuQuantity">
          <br>
          <label for="size">Select Size:</label>
          <select class="form-control" id="size" name="size">
          <option value="small">Small</option>
          <option value="medium">Medium</option>
          <option value="large">Large</option>
          </select>
          <br>
          <label for="price">Enter Price:</label>
          <input class="form-control" type="number" placeholder="Price" name="price">
          <br>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          <button type="button" class="btn btn-primary" id="submitChange">Submit</button>
        </div>
        </div>
      </div>
      </div>
    `;

    // Append the modal to the body
    $('body').append(modalHtml);

    // Show the modal
    $('#assortingModal').modal('show');

    $('#submitChange').on('click', function() {
      var quantity = $('input[name="skuQuantity"]').val();
      var size = $('select[name="size"]').val();
      var price = $('input[name="price"]').val();

      $.ajax({
        url: '/assorting',
        type: 'POST',
        data: {
            id: id,
            quantity: quantity,
            size: size,
            price: price,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
          $('#assortingModal').modal('hide');
          $('#assortingModal').remove();
          table.ajax.reload(null, false);
          $('#messageContainer').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
        },
        error: function(xhr, status, error) {
          console.error("Error: " + error);
          $('#messageContainer').html('<div class="alert alert-danger" role="alert">' + response.message + '</div>');
        }
      });
    });

    // Remove the modal from the DOM when it's closed to avoid duplicate IDs
    $('#assortingModal').on('hidden.bs.modal', function () {
        $(this).remove();
    });
}

function openChangeCardModal(productId, id) {
    var modalHtml = `
      <div class="modal fade" id='changeCardModal' tabindex="-1" aria-labelledby="changeCardModal" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5" id="changeCardModal">Change Card</h1>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              You are Changing Cards for <b>` + productId + `</b>
              <br>
              <input class="form-control"  type="number" name="quantity" placeholder="Quantity" >
              <br>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <button type="button" class="btn btn-primary" id='submitChange'>Submit</button>
            </div>
          </div>
        </div>
      </div>
    `;

    // Append the modal to the body
    $('body').append(modalHtml);

    // Show the modal
    $('#changeCardModal').modal('show');

    $('#submitChange').on('click', function() {
      var quantity = $('input[name="quantity"]').val();

      $.ajax({
        url: '/changeCard',
        type: 'POST',
        data: {
            id: id,
            quantity: quantity,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
          $('#changeCardModal').modal('hide');
          $('#changeCardModal').remove();
          table.ajax.reload(null, false);
          alert("Card changed successfully");
        },
        error: function(xhr, status, error) {
          console.error("Error: " + error);
        }
      });
    });

    // Remove the modal from the DOM when it's closed to avoid duplicate IDs
    $('#changeCardModal').on('hidden.bs.modal', function () {
        $(this).remove();
    });
}

function openClearanceModal(productId, id) {
    var modalHtml = `
      <div class="modal fade" id='clearanceModal' tabindex="-1" aria-labelledby="clearanceModal" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5" id="clearanceModal">Clearance</h1>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              You are Clearing for <b>` + productId + `</b>
              <br>
              <input class="form-control"  type="number" name="quantity" placeholder="Quantity" >
              <br>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <button type="submit" class="btn btn-primary" id="submitChange">Submit</button>
            </div>
          </div>
        </div>
      </div>
    `;

    // Append the modal to the body
    $('body').append(modalHtml);

    // Show the modal
    $('#clearanceModal').modal('show');

    $('#submitChange').on('click', function() {
      var quantity = $('input[name="quantity"]').val();

      $.ajax({
        url: '/clearance',
        type: 'POST',
        data: {
            id: id,
            quantity: quantity,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
          $('#clearanceModal').modal('hide');
          $('#clearanceModal').remove();
          table.ajax.reload(null, false);
          alert("Cleared successfully");
        },
        error: function(xhr, status, error) {
          console.error("Error: " + error);
        }
      });
    });
    
    // Remove the modal from the DOM when it's closed to avoid duplicate IDs
    $('#clearanceModal').on('hidden.bs.modal', function () {
        $(this).remove();
    });
}

function openDestroyModal(productId, id) {
    // Create the modal HTML dynamically
    var modalHtml = `
    <form action="/destroy" method="POST">
      {% csrf_token %}
        <div class="modal fade" id='destroyModal' tabindex="-1" aria-labelledby="destroyModal" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5" id="destroyModal">Destroy</h1>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              You are Destroying for <b>` + productId + `</b>
              <br>
              <input class="form-control"  type="number" name="quantity" placeholder="Quantity of products to dispose" >
              <br>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <button type="button" class="btn btn-primary" id="submitChange">Submit</button>
            </div>
          </div>
        </div>
      </div>
    </form>
    `;

    // Append the modal to the body
    $('body').append(modalHtml);

    // Show the modal
    $('#destroyModal').modal('show');

    $('#submitChange').on('click', function() {
      var quantity = $('input[name="quantity"]').val();

      $.ajax({
        url: '/destroy',
        type: 'POST',
        data: {
            id: id,
            quantity: quantity,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
          $('#destroyModal').modal('hide');
          $('#destroyModal').remove();
          table.ajax.reload(null, false);
          alert("Destroyed successfully");
        },
        error: function(xhr, status, error) {
          console.error("Error: " + error);
        }
      });
    });

    // Remove the modal from the DOM when it's closed to avoid duplicate IDs
    $('#destroyModal').on('hidden.bs.modal', function () {
        $(this).remove();
    });
}

function openInspectionModal(productId, id) {
    // Create the modal HTML dynamically
    var modalHtml = `
      <div class="modal fade" id='inspectionModal' tabindex="-1" aria-labelledby="inspectionModal" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5" id="inspectionModal">Inspection</h1>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              You are Inspecting for <b>` + productId + `</b>
              <br>
              <input class="form-control" type="number" placeholder="Number of products to inspect" name="quantity" min="1"/>
              <br>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <button type="button" class="btn btn-primary" id="submitChange">Submit</button>
            </div>
          </div>
        </div>
      </div>
    `;

    // Append the modal to the body
    $('body').append(modalHtml);

    // Show the modal
    $('#inspectionModal').modal('show');

    $('#submitChange').on('click', function() {
      var quantity = $('input[name="quantity"]').val();

      $.ajax({
        url: '/inspection',
        type: 'POST',
        data: {
            id: id,
            quantity: quantity,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
          $('#inspectionModal').modal('hide');
          $('#inspectionModal').remove();
          table.ajax.reload(null, false);
          $('#messageContainer').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
        },
        error: function(xhr, status, error) {
          console.error("Error: " + error);
          $('#messageContainer').html('<div class="alert alert-danger" role="alert">' + response.message + '</div>');
        }
      });
    });

    // Remove the modal from the DOM when it's closed to avoid duplicate IDs
    $('#inspectionModal').on('hidden.bs.modal', function () {
        $(this).remove();
    });
}

function openPhotoModal(productId, id) {
    // Create the modal HTML dynamically
    var modalHtml = `
      <div class="modal fade" id='photoModal' tabindex="-1" aria-labelledby="photoModal" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5" id="photoModal">Photo</h1>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              You are taking Photos for <b>` + productId + `</b>
              <br>
              <input class="form-control" type="number" placeholder="Number of photos to be taken" name="quantity" min="1"/>
              <br>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <button type="submit" class="btn btn-primary" id="submitChange">Submit</button>
            </div>
          </div>
        </div>
      </div>
    `;

    // Append the modal to the body
    $('body').append(modalHtml);

    // Show the modal
    $('#photoModal').modal('show');

    $('#submitChange').on('click', function() {
      var quantity = $('input[name="quantity"]').val();

      $.ajax({
        url: '/photo',
        type: 'POST',
        data: {
            id: id,
            quantity: quantity,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
          $('#photoModal').modal('hide');
          $('#photoModal').remove();
          table.ajax.reload(null, false);
          $('#messageContainer').html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
        },
        error: function(xhr, status, error) {
          console.error("Error: " + error);
          $('#messageContainer').html('<div class="alert alert-danger" role="alert">' + response.message + '</div>');
        }
      });
    });

    // Remove the modal from the DOM when it's closed to avoid duplicate IDs
    $('#photoModal').on('hidden.bs.modal', function () {
        $(this).remove();
    });
}