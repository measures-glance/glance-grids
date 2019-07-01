---
layout: default
---

# Parameters

## Parameter References
* crs - "Coordinate Reference System"
* ul - "Upper left X/Y"
* size - "Tile size X/Y"
* res - "Pixel size X/Y"
* limits - "Tile grid limits (row range, column range)"
* name - "Grid name"

## CRS Table
<table>
<th>Continent Name</th>
<th>CRS</th>
{% for continent in site.data.GLANCE_param %}
    {% assign cont_name = continent[0] %}
    {% assign cont_data = continent[1] %}
    <tr>
        <td>{{ cont_name }}</td>
        <td>{{ cont_data.crs }}</td>
    </tr>
    
    
{% endfor %}
</table>


## Individual Continents
{% for continent in site.data.GLANCE_param %}
{% assign cont_name = continent[0] %}
{% assign cont_data = continent[1] %}
### {{ cont_name }}
<table>
    
	<th>name</th>
    <th>Upper-Left</th>
    <th>crs</th>
    <th>Resolution</th>
    <th>Size</th>
    <th>Limits</th>
    <tr>
    	<td>{{ cont_data.name }}</td>
    	<td>
            <ul>
                <li>{{ cont_data.ul[0] }}</li>
                <li>{{ cont_data.ul[1] }}</li>
            </ul>    	
    	</td>
    	<td>{{cont_data.crs}}</td>
    	<td>
            <ul>
                <li>{{ cont_data.res[0] }}</li>
                <li>{{ cont_data.res[1] }}</li>
            </ul>    	
    	</td>
    	<td>
            <ul>
                <li>{{ cont_data.size[0] }}</li>
                <li>{{ cont_data.size[1] }}</li>
            </ul>    	
    	</td>
    	<td>
            <ul>
                <li>({{ cont_data.limits[0][0] }} , {{ cont_data.limits[0][1] }})</li>
                <li>({{ cont_data.limits[1][0] }} , {{ cont_data.limits[1][1] }})</li>
            </ul>    	
    	</td>
    </tr>

</table>
{% endfor %}
