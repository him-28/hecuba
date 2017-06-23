
#include "TupleRow.h"


TupleRow::TupleRow(std::shared_ptr <const std::vector<ColumnMeta>> metas,
                   uint16_t payload_size, void *buffer) {
    this->metadata = metas;
    //create data structures
    payload = std::shared_ptr<void>(buffer,
                                    [metas](void *ptr) {
                                        for (uint16_t i=0; i<metas->size(); ++i) {
                                            switch ( metas->at(i).type) {
                                                case CASS_VALUE_TYPE_BLOB:
                                                case CASS_VALUE_TYPE_TEXT:
                                                case CASS_VALUE_TYPE_VARCHAR:
                                                case CASS_VALUE_TYPE_UUID:
                                                case CASS_VALUE_TYPE_ASCII: {
                                                    int64_t *addr = (int64_t * )((char *) ptr +  metas->at(i).position);
                                                    char *d = reinterpret_cast<char *>(*addr);
                                                    free(d);
                                                    break;
                                                }
                                                default:
                                                    break;
                                            }
                                        }
                                        free(ptr);

                                    });

    this->payload_size = payload_size;
    this->null_values = 0;
}


TupleRow::TupleRow(const TupleRow &t) {
    this->payload_size=t.payload_size;
    this->payload = t.payload;
    this->metadata = t.metadata;
    this->null_values = t.null_values;
}

TupleRow::TupleRow(const TupleRow *t) {
    this->payload_size=t->payload_size;
    this->payload = t->payload;
    this->metadata = t->metadata;
    this->null_values = t->null_values;
}

TupleRow::TupleRow(TupleRow &t) {
    this->payload_size=t.payload_size;
    this->payload = t.payload;
    this->metadata = t.metadata;
    this->null_values = t.null_values;
}

TupleRow::TupleRow(TupleRow *t) {
    this->payload_size=t->payload_size;
    this->payload = t->payload;
    this->metadata = t->metadata;
    this->null_values = t->null_values;
}

TupleRow &TupleRow::operator=(const TupleRow &t) {
    this->payload_size=t.payload_size;
    this->payload = t.payload;
    this->metadata = t.metadata;
    this->null_values = t.null_values;
    return *this;
}

TupleRow &TupleRow::operator=(TupleRow &t) {
    this->payload_size=t.payload_size;
    this->payload = t.payload;
    this->metadata = t.metadata;
    this->null_values = t.null_values;
    return *this;
}

bool operator<(const TupleRow &lhs, const TupleRow &rhs) {
    if (lhs.payload_size != rhs.payload_size) return lhs.payload_size < rhs.payload_size;
    if (lhs.metadata != rhs.metadata) return lhs.metadata < rhs.metadata;
    if (lhs.null_values!=rhs.null_values) return lhs.null_values < rhs.null_values;
    return memcmp(lhs.payload.get(), rhs.payload.get(), lhs.payload_size) < 0;
}

bool operator>(const TupleRow &lhs, const TupleRow &rhs) {
    return rhs < lhs;
}

bool operator<=(const TupleRow &lhs, const TupleRow &rhs) {

    if (lhs.payload_size != rhs.payload_size) return lhs.payload_size < rhs.payload_size;
    if (lhs.metadata != rhs.metadata) return lhs.metadata < rhs.metadata;
    if (lhs.null_values!=rhs.null_values) return lhs.null_values < rhs.null_values;
    return memcmp(lhs.payload.get(), rhs.payload.get(), lhs.payload_size) <= 0;
}

bool operator>=(const TupleRow &lhs, const TupleRow &rhs) {
    return rhs <= lhs;
}

bool operator==(const TupleRow &lhs, const TupleRow &rhs) {

    if (lhs.payload_size != rhs.payload_size) return lhs.payload_size < rhs.payload_size;
    if (lhs.metadata != rhs.metadata) return lhs.metadata < rhs.metadata;
    if (lhs.null_values!=rhs.null_values) return lhs.null_values < rhs.null_values;
    return memcmp(lhs.payload.get(), rhs.payload.get(), lhs.payload_size) == 0;
}
