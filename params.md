---
layout: default
---

# Parameters

## Parameter References
* name - "Grid name"
* ul - "Upper left X/Y"
* crs - "Coordinate Reference System"
* res - "Pixel size X/Y" 
* size - "Tile size X/Y"
* limits - "Tile grid limits (row range, column range)"

## CRS Table
<table style="table-layout: fixed; width: 100%">
<th>Continent Name</th>
<th>CRS</th>
{% for continent in site.data.GLANCE_param %}
    {% assign cont_name = continent[0] %}
    {% assign cont_data = continent[1] %}
    <tr>
        <td>{{ cont_name }}</td>
        <td style="word-break:break-all;">{{ cont_data.crs }}</td>
    </tr>
    
    
{% endfor %}
</table>


## Individual Continents
{% for continent in site.data.GLANCE_param %}
{% assign cont_name = continent[0] %}
{% assign cont_data = continent[1] %}
### {{ cont_name }}
<table style="table-layout: fixed; width: 100%">
    <tr>
	    <th>name</th>
	    <td>{{ cont_data.name }}</td>
	</tr>
	<tr>
        <th>ul</th>
        <td>
            <ul>
                <li>{{ cont_data.ul[0] }}</li>
                <li>{{ cont_data.ul[1] }}</li>
            </ul>    	
        </td>
    </tr>
    <tr>
        <th>crs</th>
        <td style="word-break:break-all;">{{cont_data.crs}}</td>
    </tr>
    <tr>
        <th>res</th>
        <td>
            <ul>
                <li>{{ cont_data.res[0] }}</li>
                <li>{{ cont_data.res[1] }}</li>
            </ul>    	
    	</td>
    </tr>
    <tr>
        <th>size</th>
        <td>
            <ul>
                <li>{{ cont_data.size[0] }}</li>
                <li>{{ cont_data.size[1] }}</li>
            </ul>    	
    	</td>
    </tr>
    <tr>
    <th>limits</th>
    <td>
            <ul>
                <li>({{ cont_data.limits[0][0] }} , {{ cont_data.limits[0][1] }})</li>
                <li>({{ cont_data.limits[1][0] }} , {{ cont_data.limits[1][1] }})</li>
            </ul>    	
    	</td>
    </tr>

</table>
{% endfor %}
