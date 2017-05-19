#import pydevd

class table_compute(object):
    def __init__(self):
        self.table = {}
        self.IPRs = {'xl':5,'lg':4,'md':3,'sm':2}  # Items Por Fila (xs no usa tablas)
        self.cCRPB = { 's':[1,1], 'm':[2,2] } # Columnas y Filas Por Banner
	self.IPR = 'lg'
            
    def _get_banner_size(self, banner):
        opt = banner.product_id.link_size.lower() if banner.product_id.link_size else "s"
        return self.cCRPB[opt] if self.cCRPB.has_key(opt) else self.cCRPB['s']

    def _check_place(self, posx, posy, sizex, sizey):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx+x>=self.IPR:
                    res = False
                    break
                row = self.table.setdefault(posy+y, {})
                if row.setdefault(posx+x) is not None:
                    res = False
                    break
            for x in range(self.IPR):
                self.table[posy+y].setdefault(x, None)
        return res

    def process_home(self, banners, tam):
        # Compute banners positions on the grid
        #pydevd.settrace("10.0.3.1")
        minpos = 0
        index = 0
        maxy = 0
	self.IPR = self.IPRs.get(tam)
        #pydevd.settrace("10.0.3.1")	
	for banner in banners:            
	    csize = self._get_banner_size(banner)
	    x = min(max(csize[0], 1), self.IPR)
	    y = min(max(csize[1], 1), self.IPR)

	    pos = minpos
	    while not self._check_place(pos%self.IPR, pos/self.IPR, x, y):
	        pos += 1

	    if x==1 and y==1:   # simple heuristic for CPU optimization
	        minpos = pos/self.IPR

	    for y2 in range(y):
	        for x2 in range(x):
	                self.table[(pos/self.IPR)+y2][(pos%self.IPR)+x2] = False
	    self.table[pos/self.IPR][pos%self.IPR] = {
	        'banner': banner,
	        'x':x, 'y': y,
	        'class': ""
	    }

	    maxy=max(maxy,y+(pos/self.IPR))
	    index += 1

        # Format table according to HTML needs
        rows = self.table.items()
        rows.sort()
        rows = map(lambda x: x[1], rows)
        for col in range(len(rows)):
            cols = rows[col].items()
            cols.sort()
            x += len(cols)
            rows[col] = [c for c in map(lambda x: x[1], cols) if c != False]

        return rows
    
    def process_directory(self, banners_directorio):
        # Compute establishments positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        
        for banner in banners_directorio:
            #csize = self._get_banner_size(banner.contract_product) if banner.contract_product else [1 , 1]
            csize = self.cCRPB['s']
            x = min(max(csize[0], 1), self.IPR)
            y = min(max(csize[1], 1), self.IPR)
	    self.IPR = self.IPRs.get('lg')
            pos = minpos
            while not self._check_place(pos%self.IPR, pos/self.IPR, x, y):
                pos += 1

            if x==1 and y==1:   # simple heuristic for CPU optimization
                minpos = pos/self.IPR

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos/self.IPR)+y2][(pos%self.IPR)+x2] = False
            self.table[pos/self.IPR][pos%self.IPR] = {
                'establishment': banner.establishment,
                'contract_product': banner.contract_product,
                'events': banner.events,
                'x':x, 'y': y,
                'class': ""
            }

            maxy=max(maxy,y+(pos/self.IPR))
            index += 1

        # Format table according to HTML needs
        rows = self.table.items()
        rows.sort()
        rows = map(lambda x: x[1], rows)
        for col in range(len(rows)):
            cols = rows[col].items()
            cols.sort()
            x += len(cols)
            rows[col] = [c for c in map(lambda x: x[1], cols) if c != False]

        return rows
    
    def process_products_establishment(self, products):
        # Compute establishments positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        for product in products:
            #csize = self._get_banner_size(banner.contract_product) if banner.contract_product else [1 , 1]
            csize = self.cCRPB['s']
            x = min(max(csize[0], 1), self.IPR)
            y = min(max(csize[1], 1), self.IPR)

            pos = minpos
            while not self._check_place(pos%self.IPR, pos/self.IPR, x, y):
                pos += 1

            if x==1 and y==1:   # simple heuristic for CPU optimization
                minpos = pos/self.IPR

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos/self.IPR)+y2][(pos%self.IPR)+x2] = False
            self.table[pos/self.IPR][pos%self.IPR] = {
                'product': product,
                'x':x, 'y': y,
                'class': ""
            }

            maxy=max(maxy,y+(pos/self.IPR))
            index += 1

        # Format table according to HTML needs
        rows = self.table.items()
        rows.sort()
        rows = map(lambda x: x[1], rows)
        for col in range(len(rows)):
            cols = rows[col].items()
            cols.sort()
            x += len(cols)
            rows[col] = [c for c in map(lambda x: x[1], cols) if c != False]

        return rows
